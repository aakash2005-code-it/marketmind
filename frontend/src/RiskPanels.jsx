import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

const CONFLICT_TITLES = {
  conflict: "Signals disagree",
  agree: "Signals agree",
  aligned: "No opposing signals",
  weak: "Weak evidence",
};

export function SignalConflict({ data }) {
  if (!data) return null;
  return (
    <div className={`conflict-banner conflict-${data.status}`}>
      <div className="conflict-head">
        <strong>{CONFLICT_TITLES[data.status] || "Signal check"}</strong>
        <div className="conflict-chips">
          {Object.entries(data.labels).map(([key, label]) => (
            <span key={key} className={`conflict-chip chip-${label}`}>
              {key}: {label}
            </span>
          ))}
        </div>
      </div>
      <p>{data.message}</p>
      <small>
        A signal counts as leaning when the technical model probability is at least 52.5%, the fundamental
        rule score is at least half of its maximum, or the headline balance is at least 10%. These
        cutoffs are judgment calls.
      </small>
    </div>
  );
}

export function StressTestPanel({ ticker }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    setError(null);
    setLoading(true);
    axios
      .get(`${API}/stress-test/${encodeURIComponent(ticker)}`)
      .then((res) => {
        if (!cancelled) setData(res.data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.response?.data?.detail || "Could not load the stress test.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [ticker]);

  const barWidth = (pct) => `${Math.min(Math.abs(pct) / 70, 1) * 100}%`;

  return (
    <div className="panel">
      <h3>Stress test <span className="card-tag">Past market shocks</span></h3>
      {loading && <p className="panel-note">Loading historical shocks…</p>}
      {error && <p className="error">{error}</p>}
      {data && data.available === false && <p className="panel-note">{data.note}</p>}
      {data && data.available && (
        <>
          <p className="panel-note">{data.summary}</p>
          <div className="stress-list">
            {data.windows.map((w) => (
              <div className="stress-row" key={w.name}>
                <div className="stress-title">
                  <strong>{w.name}</strong>
                  <small>{w.start} to {w.end}</small>
                </div>
                {w.covered ? (
                  <>
                    <div className="stress-bars">
                      <div className="stress-bar-line">
                        <span>This stock</span>
                        <div className="stress-track"><div className="stress-fill stock" style={{ width: barWidth(w.stock_drawdown_pct) }} /></div>
                        <em>{w.stock_drawdown_pct}%</em>
                      </div>
                      <div className="stress-bar-line">
                        <span>{data.benchmark_label}</span>
                        <div className="stress-track"><div className="stress-fill bench" style={{ width: barWidth(w.benchmark_drawdown_pct) }} /></div>
                        <em>{w.benchmark_drawdown_pct}%</em>
                      </div>
                    </div>
                    <small className="stress-recovery">
                      {w.recovered
                        ? `Regained its prior peak ${w.recovery_days} trading days after the low (${w.trough_date}).`
                        : `Had not regained its prior peak by the end of the available data (low on ${w.trough_date}).`}
                    </small>
                  </>
                ) : (
                  <small className="stress-recovery">Not enough price history for this stock in this window.</small>
                )}
              </div>
            ))}
          </div>
          <p className="panel-note stress-footnote">{data.note}</p>
        </>
      )}
    </div>
  );
}

export function CalibrationPanel({ probability }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = async (refresh = false) => {
    const token = localStorage.getItem("mm_token");
    if (!token) {
      setError("Please log in to load the reliability data.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API}/calibration`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { refresh },
      });
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not compute the reliability data right now.");
    } finally {
      setLoading(false);
    }
  };

  const p = probability === null || probability === undefined ? null : probability * 100;
  const match =
    data && data.available && p !== null
      ? data.bins.find((b) => p >= b.lower_pct && p < b.upper_pct + (b.upper_pct >= 100 ? 1 : 0))
      : null;

  return (
    <div className="panel">
      <h3>How reliable is the technical model? <span className="card-tag">Calibration</span></h3>
      <p className="panel-note">
        When the model says "60% chance of rising", how often did the price actually rise? This checks the
        model's stated probabilities against what happened on data it never trained on.
      </p>

      {!data && (
        <button className="preset-btn" onClick={() => load(false)} disabled={loading}>
          {loading ? "Computing (the first run can take a minute or two)…" : "Load reliability data"}
        </button>
      )}
      {error && <p className="error">{error}</p>}
      {data && data.available === false && <p className="error">{data.note}</p>}

      {data && data.available && (
        <>
          <div className="cal-verdict">
            {p === null && <p>No technical probability is available for this stock.</p>}
            {p !== null && match && match.reliable && (
              <p>
                For this stock the technical model gave <strong>{p.toFixed(1)}%</strong>. In out-of-sample
                testing, when it said <strong>{match.label}</strong>, the price rose{" "}
                <strong>{match.actual_pct}%</strong> of the time ({match.count} cases).
              </p>
            )}
            {p !== null && (!match || !match.reliable) && (
              <p>
                For this stock the technical model gave <strong>{p.toFixed(1)}%</strong>, but too few testing
                cases fall in that range to say how reliable it is.
              </p>
            )}
          </div>

          <table className="cal-table">
            <thead>
              <tr><th>Model said</th><th>Cases</th><th>Average stated</th><th>Actually rose</th></tr>
            </thead>
            <tbody>
              {data.bins.map((b) => (
                <tr key={b.label} className={match && match.label === b.label ? "cal-active" : ""}>
                  <td>{b.label}</td>
                  <td>{b.count}</td>
                  <td>{b.predicted_pct === null ? "n/a" : `${b.predicted_pct}%`}</td>
                  <td>{b.actual_pct === null ? "n/a" : `${b.actual_pct}%`}{!b.reliable && b.count > 0 ? " (few cases)" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <p className="panel-note cal-summary">
            Average gap between stated and actual: <strong>{data.ece_pct} points</strong>. Prices rose{" "}
            <strong>{data.base_rate_pct}%</strong> of the time overall in training. Brier score{" "}
            <strong>{data.brier_model}</strong> versus <strong>{data.brier_baseline}</strong> for always
            predicting that base rate (lower is better):{" "}
            {data.brier_model < data.brier_baseline
              ? "the model adds a small amount of information beyond the base rate."
              : "the model is no better than the base rate on this measure."}
          </p>
          <ul className="track-notes">
            {data.notes.map((n, i) => <li key={i}>{n}</li>)}
          </ul>
          <button className="preset-btn" onClick={() => load(true)} disabled={loading}>
            {loading ? "Re-running…" : "Re-run with fresh data"}
          </button>
        </>
      )}
    </div>
  );
}