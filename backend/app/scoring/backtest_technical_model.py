import pandas as pd
import xgboost as xgb
from sklearn.metrics import classification_report
from app.scoring.train_technical_model import build_dataset, FEATURES

def walk_forward_backtest(tickers: list[str], n_splits: int = 4):
    all_data = []
    for t in tickers:
        try:
            data = build_dataset(t, period="5y")
            data["ticker"] = t
            all_data.append(data)
        except Exception as e:
            print(f"Skipped {t}: {e}")

    full_df = pd.concat(all_data).sort_index()
    full_df = full_df.reset_index(drop=True)

    fold_size = len(full_df) // (n_splits + 1)
    all_preds, all_actuals = [], []

    for i in range(1, n_splits + 1):
        train_end = fold_size * i
        test_end = fold_size * (i + 1)

        train = full_df.iloc[:train_end]
        test = full_df.iloc[train_end:test_end]
        if len(test) == 0:
            continue

        X_train, y_train = train[FEATURES], train["target"]
        X_test, y_test = test[FEATURES], test["target"]

        pos = (y_train == 1).sum()
        neg = (y_train == 0).sum()
        spw = neg / pos if pos > 0 else 1

        model = xgb.XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            scale_pos_weight=spw, eval_metric="logloss",
        )
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        all_preds.extend(preds)
        all_actuals.extend(y_test)

        print(f"\n--- Fold {i} (train rows: {len(train)}, test rows: {len(test)}) ---")
        print(classification_report(y_test, preds, target_names=["Down", "Up"]))

    print("\n=== OVERALL WALK-FORWARD RESULTS ===")
    print(classification_report(all_actuals, all_preds, target_names=["Down", "Up"]))

if __name__ == "__main__":
    tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "WMT",
        "JNJ", "PG", "HD", "DIS", "NFLX", "BAC", "XOM", "PFE", "KO", "CSCO",
    ]
    walk_forward_backtest(tickers)