from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import SearchHistory, User, WatchlistItem
from app.scoring.quick_analysis import quick_verdict

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


def _iso(dt):
    if dt is None:
        return None
    return dt.replace(microsecond=0).isoformat() + "Z"


def _serialize(item: WatchlistItem) -> dict:
    return {
        "ticker": item.ticker,
        "last_verdict": item.last_verdict,
        "previous_verdict": item.previous_verdict,
        "last_score": item.last_score,
        "last_price": item.last_price,
        "added_at": _iso(item.added_at),
        "last_checked_at": _iso(item.last_checked_at),
        "changed_at": _iso(item.changed_at),
    }


@router.get("")
def list_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == current_user.id)
        .order_by(WatchlistItem.added_at.desc())
        .all()
    )
    return {"items": [_serialize(i) for i in items]}


# NOTE: this route is declared before "/{ticker}" so "check" is not treated as a ticker.
@router.post("/check")
def check_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == current_user.id)
        .all()
    )

    changes = []
    failed = []

    for item in items:
        try:
            fresh = quick_verdict(item.ticker)
        except Exception:
            failed.append(item.ticker)
            continue

        now = datetime.utcnow()
        if fresh["verdict"] != item.last_verdict:
            changes.append({
                "ticker": item.ticker,
                "from": item.last_verdict,
                "to": fresh["verdict"],
            })
            item.previous_verdict = item.last_verdict
            item.changed_at = now

        item.last_verdict = fresh["verdict"]
        item.last_score = fresh["investment_score"]
        item.last_price = fresh["latest_price"]
        item.last_checked_at = now

    db.commit()

    refreshed = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == current_user.id)
        .order_by(WatchlistItem.added_at.desc())
        .all()
    )
    return {
        "changes": changes,
        "failed": failed,
        "items": [_serialize(i) for i in refreshed],
    }


@router.post("/{ticker}")
def add_to_watchlist(
    ticker: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    symbol = ticker.strip().upper()

    existing = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == current_user.id, WatchlistItem.ticker == symbol)
        .first()
    )
    if existing:
        return _serialize(existing)

    latest = (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == current_user.id, SearchHistory.ticker == symbol)
        .order_by(SearchHistory.searched_at.desc())
        .first()
    )
    if latest is None:
        raise HTTPException(
            status_code=400,
            detail="Analyze this stock first so a baseline verdict exists.",
        )

    item = WatchlistItem(
        user_id=current_user.id,
        ticker=symbol,
        last_verdict=latest.verdict,
        last_score=latest.investment_score,
        last_price=latest.latest_price,
        last_checked_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


@router.delete("/{ticker}")
def remove_from_watchlist(
    ticker: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    symbol = ticker.strip().upper()
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == current_user.id, WatchlistItem.ticker == symbol)
        .first()
    )
    if item:
        db.delete(item)
        db.commit()
    return {"removed": symbol}