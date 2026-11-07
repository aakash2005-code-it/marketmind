import { useState, useEffect } from "react";
import ChatBot from "./ChatBot";
import axios from "axios";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, Legend,
} from "recharts";
import "./App.css";
import "./dashboard.css";
import AuthModal from "./Auth";
import { SignalConflict, CalibrationPanel, StressTestPanel } from "./RiskPanels";

function Logo() {
  return (
    <div className="logo">
      <span className="logo-bars">
        <span className="bar bar-1" />
        <span className="bar bar-2" />
        <span className="bar bar-3" />
      </span>
      MarketMind
    </div>
  );
}

const VERDICT_COLOR = { Buy: "#0F9D6E", Hold: "#E0A100", Avoid: "#E0293E" };

const DEFAULT_WEIGHTS = { tech: 40, fund: 30, sent: 30 };
const WEIGHT_PRESETS = [
  { name: "Conservative", weights: { tech: 20, fund: 60, sent: 20 } },
  { name: "Balanced (default)", weights: DEFAULT_WEIGHTS },
  { name: "Trader", weights: { tech: 60, fund: 10, sent: 30 } },
];

const RESULT_TABS = [
  ["overview", "Overview"],
  ["explain", "Explainability"],
  ["fundamentals", "Fundamentals"],
  ["risk", "Risk"],
];

const fmtPct = (v) => (v === null || v === undefined ? "n/a" : `${v > 0 ? "+" : ""}${v}%`);

// Mirrors the verdict thresholds and confidence formula in the backend combiner
function recompute(breakdown, w) {
  const total = w.tech + w.fund + w.sent;
  if (total <= 0) return null;
  const wt = w.tech / total;
  const wf = w.fund / total;
  const ws = w.sent / total;
  const final = wt * breakdown.technical + wf * breakdown.fundamental + ws * breakdown.sentiment;
  let verdict = "Hold";
  if (final > 0.25) verdict = "Buy";
  else if (final < -0.25) verdict = "Avoid";
  const confidence = Math.min(Math.abs(final) * 2, 1);
  return { final, verdict, confidence, weights: { tech: wt, fund: wf, sent: ws } };
}

function VerdictDonut({ verdict, confidence }) {
  const color = VERDICT_COLOR[verdict] || "#6B7280";
  const data = [
    { value: confidence * 100 },
    { value: 100 - confidence * 100 },
  ];
  return (
    <div className="donut-wrap">
      <ResponsiveContainer width={150} height={150}>
        <PieChart>
          <Pie
            data={data}
            innerRadius={52}
            outerRadius={68}
            startAngle={90}
            endAngle={-270}
            dataKey="value"
            stroke="none"
          >
            <Cell fill={color} />
            <Cell fill="#EDEFF3" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="donut-center">
        <strong style={{ color }}>{verdict}</strong>
        <span>{(confidence * 100).toFixed(0)}% conf.</span>
      </div>
    </div>
  );
}

function App() {
  const [ticker, setTicker] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [pastSearches, setPastSearches] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [user, setUser] = useState(() => localStorage.getItem("mm_email"));
  const [advisorData, setAdvisorData] = useState(null);
  const [advisorLoading, setAdvisorLoading] = useState(false);
  const [tape, setTape] = useState([]);
  const [indiaTape, setIndiaTape] = useState([]);
  const [activeMarket, setActiveMarket] = useState("US"); // "US" | "IN"
  const [descExpanded, setDescExpanded] = useState(false);
  const [financialsData, setFinancialsData] = useState(null);
  const [peersData, setPeersData] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [watchlist, setWatchlist] = useState([]);
  const [showWatchlist, setShowWatchlist] = useState(false);
  const [watchlistBusy, setWatchlistBusy] = useState(false);
  const [watchlistMsg, setWatchlistMsg] = useState(null);
  const [trackRecord, setTrackRecord] = useState(null);
  const [trackLoading, setTrackLoading] = useState(false);
  const [trackError, setTrackError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const authConfig = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem("mm_token")}` },
  });

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/ticker-tape")
      .then((res) => setTape(res.data.tape))
      .catch(() => {});
    axios.get("http://127.0.0.1:8000/ticker-tape-india")
      .then((res) => setIndiaTape(res.data.tape))
      .catch(() => {});
  }, []);

  const fetchWatchlist = async () => {
    const token = localStorage.getItem("mm_token");
    if (!token) return;
    try {
      const res = await axios.get("http://127.0.0.1:8000/watchlist", authConfig());
      setWatchlist(res.data.items);
    } catch (err) {
      if (err.response?.status === 401) setShowAuth(true);
    }
  };

  useEffect(() => {
    if (user) fetchWatchlist();
    else setWatchlist([]);
  }, [user]);

  const openWatchlist = () => {
    setWatchlistMsg(null);
    setShowWatchlist(true);
    fetchWatchlist();
  };

  const addToWatchlist = async () => {
    if (!result) return;
    const token = localStorage.getItem("mm_token");
    if (!token) {
      setShowAuth(true);
      return;
    }
    try {
      await axios.post(
        `http://127.0.0.1:8000/watchlist/${encodeURIComponent(result.ticker)}`,
        {},
        authConfig()
      );
      await fetchWatchlist();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not add to the watchlist.");
    }
  };

  const removeFromWatchlist = async (symbol) => {
    try {
      await axios.delete(
        `http://127.0.0.1:8000/watchlist/${encodeURIComponent(symbol)}`,
        authConfig()
      );
      await fetchWatchlist();
    } catch (err) {
      if (err.response?.status === 401) setShowAuth(true);
    }
  };

  const checkWatchlist = async () => {
    setWatchlistBusy(true);
    setWatchlistMsg(null);
    try {
      const res = await axios.post("http://127.0.0.1:8000/watchlist/check", {}, authConfig());
      setWatchlist(res.data.items);
      const n = res.data.changes.length;
      const failedCount = res.data.failed.length;
      let msg = n === 0
        ? "No verdict changes since your last check."
        : `${n} verdict change${n > 1 ? "s" : ""} detected.`;
      if (failedCount > 0) {
        msg += ` ${failedCount} stock${failedCount > 1 ? "s" : ""} could not be re-checked right now.`;
      }
      setWatchlistMsg(msg);
    } catch (err) {
      if (err.response?.status === 401) setShowAuth(true);
      else setWatchlistMsg("Could not re-check the watchlist right now.");
    } finally {
      setWatchlistBusy(false);
    }
  };

  const fetchTrackRecord = async (refresh = false) => {
    const token = localStorage.getItem("mm_token");
    if (!token) {
      setShowAuth(true);
      return;
    }
    setTrackLoading(true);
    setTrackError(null);
    try {
      const res = await axios.get("http://127.0.0.1:8000/track-record", {
        headers: { Authorization: `Bearer ${token}` },
        params: { refresh },
      });
      setTrackRecord(res.data);
    } catch (err) {
      if (err.response?.status === 401) setShowAuth(true);
      else setTrackError(err.response?.data?.detail || "Could not run the backtest right now.");
    } finally {
      setTrackLoading(false);
    }
  };

  const fetchAdvisor = async () => {
    const token = localStorage.getItem("mm_token");
    if (!token) {
      setShowAuth(true);
      return;
    }
    setAdvisorLoading(true);
    try {
      const res = await axios.get("http://127.0.0.1:8000/portfolio-advisor", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAdvisorData(res.data);
    } catch (err) {
      if (err.response?.status === 401) setShowAuth(true);
    } finally {
      setAdvisorLoading(false);
    }
  };

  const handleTickerInputChange = (value) => {
    setTicker(value);

    if (value.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    clearTimeout(window._tickerSearchTimeout);
    window._tickerSearchTimeout = setTimeout(() => {
      axios.get("http://127.0.0.1:8000/search-ticker", { params: { q: value } })
        .then((res) => {
          setSuggestions(res.data.results);
          setShowSuggestions(res.data.results.length > 0);
        })
        .catch(() => setSuggestions([]));
    }, 400);
  };

  const selectSuggestion = (symbol) => {
    setTicker(symbol);
    setSuggestions([]);
    setShowSuggestions(false);
  };

  const handleAnalyze = async () => {
    if (!ticker) return;

    const token = localStorage.getItem("mm_token");
    if (!token) {
      setShowAuth(true);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setHistory(null);
    setPeersData(null);
    setFinancialsData(null);
    setWeights(DEFAULT_WEIGHTS);
    setActiveTab("overview");

    const symbol = activeMarket === "IN" ? ticker.trim() : ticker.trim().toUpperCase();
    const authHeader = { headers: { Authorization: `Bearer ${token}` } };

    try {
      const [analyzeRes, historyRes] = await Promise.all([
        axios.get(`http://127.0.0.1:8000/analyze/${encodeURIComponent(symbol)}`, authHeader),
        axios.get(`http://127.0.0.1:8000/history/${encodeURIComponent(symbol)}`),
      ]);
      setResult(analyzeRes.data);
      setHistory(historyRes.data.history);

      const sector = analyzeRes.data.sector;
      const resolvedTicker = analyzeRes.data.ticker;
      axios.get(`http://127.0.0.1:8000/peers/${encodeURIComponent(resolvedTicker)}`, { params: { sector } })
        .then((res) => setPeersData(res.data.peers))
        .catch(() => setPeersData([]));

      axios.get(`http://127.0.0.1:8000/financials/${encodeURIComponent(resolvedTicker)}`)
        .then((res) => setFinancialsData(res.data.quarters))
        .catch(() => setFinancialsData([]));
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Please log in again.");
        setShowAuth(true);
      } else {
        setError(err.response?.data?.detail || "Something went wrong. Make sure the company name or ticker is correct.");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    const token = localStorage.getItem("mm_token");
    if (!token) {
      setShowAuth(true);
      return;
    }
    try {
      const res = await axios.get("http://127.0.0.1:8000/my-history", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPastSearches(res.data);
      setShowHistory(true);
    } catch (err) {
      if (err.response?.status === 401) setShowAuth(true);
    }
  };

  const handleAuthSuccess = (email) => {
    setUser(email);
  };

  const handleLogout = () => {
    localStorage.removeItem("mm_token");
    localStorage.removeItem("mm_email");
    setUser(null);
  };

  const groupExplanation = (explanation) => {
    const groups = { Technical: [], Fundamental: [], Sentiment: [] };
    explanation.forEach((line) => {
      const match = line.match(/^\[(\w+)\]\s*(.*)$/);
      if (match) groups[match[1]]?.push(match[2]);
    });
    return groups;
  };

  const priceChange = history && history.length > 1
    ? (((history[history.length - 1].close - history[0].close) / history[0].close) * 100).toFixed(2)
    : null;

  const custom = result ? recompute(result.breakdown, weights) : null;
  const inWatchlist = result ? watchlist.some((w) => w.ticker === result.ticker) : false;
  const recentChanges = watchlist.filter(
    (w) => w.changed_at && Date.now() - new Date(w.changed_at).getTime() < 7 * 24 * 60 * 60 * 1000
  ).length;
  const currency = result?.currency_symbol || "$";

  return (
    <div className="page">
      {/* DUAL TICKER TAPE */}
      {(tape.length > 0 || indiaTape.length > 0) && (
        <div className="ticker-tape">
          {tape.length > 0 && (
            <div className="ticker-tape-track">
              {[...tape, ...tape].map((t, idx) => (
                <span className="tape-item" key={idx}>
                  <strong>{t.symbol}</strong>
                  <span>{t.currency || "$"}{t.price}</span>
                  <span className={t.change_pct >= 0 ? "positive" : "negative"}>
                    {t.change_pct >= 0 ? "▲" : "▼"} {Math.abs(t.change_pct)}%
                  </span>
                </span>
              ))}
            </div>
          )}
          {indiaTape.length > 0 && (
            <div className="ticker-tape-track india-tape">
              <span className="tape-india-label">NSE/BSE</span>
              {[...indiaTape, ...indiaTape].map((t, idx) => (
                <span className={`tape-item ${t.is_index ? "tape-index" : ""}`} key={idx}>
                  <strong>{t.symbol}</strong>
                  <span>₹{t.price.toLocaleString("en-IN")}</span>
                  <span className={t.change_pct >= 0 ? "positive" : "negative"}>
                    {t.change_pct >= 0 ? "▲" : "▼"} {Math.abs(t.change_pct)}%
                  </span>
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* NAVBAR */}
      <nav className="navbar">
        <Logo />
        <div className="nav-center">
          <a href="#how-it-works">How it works</a>
          <a href="#advisor">Portfolio Advisor</a>
          <a href="#track-record">Track Record</a>
        </div>
        <div className="nav-actions">
          {user ? (
            <>
              <button className="nav-login" onClick={openWatchlist}>
                Watchlist
                {recentChanges > 0 && <span className="nav-badge">{recentChanges}</span>}
              </button>
              <button className="nav-login" onClick={fetchHistory}>History</button>
              <span className="nav-user" title={user}>{user}</span>
              <button className="nav-logout" onClick={handleLogout}>Log out</button>
            </>
          ) : (
            <button className="nav-login" onClick={() => setShowAuth(true)}>Log in</button>
          )}
          <a href="#analyzer" className="nav-cta">Analyze a stock</a>
        </div>
      </nav>

      {showAuth && (
        <AuthModal
          onClose={() => setShowAuth(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      )}

      {showHistory && (
        <div className="auth-overlay" onClick={() => setShowHistory(false)}>
          <div className="auth-modal history-modal" onClick={(e) => e.stopPropagation()}>
            <button className="auth-close" onClick={() => setShowHistory(false)}>×</button>
            <h2>Your search history</h2>
            <p className="auth-sub">Every ticker you've analyzed, most recent first.</p>

            {pastSearches.length === 0 ? (
              <p className="history-empty">No searches yet. Analyze a stock to see it here.</p>
            ) : (
              <div className="history-list">
                {pastSearches.map((s, idx) => (
                  <div className="history-row" key={idx}>
                    <div className="history-ticker">{s.ticker}</div>
                    <span className={`verdict-pill pill-${s.verdict?.toLowerCase()}`}>{s.verdict}</span>
                    <div className="history-price">{s.ticker.endsWith(".NS") || s.ticker.endsWith(".BO") ? "₹" : "$"}{s.latest_price}</div>
                    <div className="history-date">{new Date(s.searched_at).toLocaleDateString()}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {showWatchlist && (
        <div className="auth-overlay" onClick={() => setShowWatchlist(false)}>
          <div className="auth-modal history-modal" onClick={(e) => e.stopPropagation()}>
            <button className="auth-close" onClick={() => setShowWatchlist(false)}>×</button>
            <h2>Your watchlist</h2>
            <p className="auth-sub">
              Re-check to see whether MarketMind's verdict has changed since you added a stock.
            </p>

            <button
              className="preset-btn"
              onClick={checkWatchlist}
              disabled={watchlistBusy || watchlist.length === 0}
            >
              {watchlistBusy ? "Re-analyzing…" : "Re-check all verdicts"}
            </button>

            {watchlistMsg && <p className="panel-note wl-msg">{watchlistMsg}</p>}

            {watchlist.length === 0 ? (
              <p className="history-empty">
                Nothing here yet. Analyze a stock and use "Add to watchlist".
              </p>
            ) : (
              <div className="wl-list">
                {watchlist.map((w) => (
                  <div className="wl-row" key={w.ticker}>
                    <div className="history-ticker">{w.ticker}</div>
                    <span className={`verdict-pill pill-${w.last_verdict?.toLowerCase()}`}>
                      {w.last_verdict}
                    </span>
                    <div className="wl-meta">
                      <div>
                        {w.ticker.endsWith(".NS") || w.ticker.endsWith(".BO") ? "₹" : "$"}
                        {w.last_price}
                      </div>
                      {w.previous_verdict && (
                        <div className="wl-change">
                          Changed from {w.previous_verdict} on {new Date(w.changed_at).toLocaleDateString()}
                        </div>
                      )}
                      <small>
                        Checked {w.last_checked_at ? new Date(w.last_checked_at).toLocaleDateString() : "never"}
                      </small>
                    </div>
                    <button className="wl-remove" onClick={() => removeFromWatchlist(w.ticker)}>
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* HERO */}
      <header className="hero">
        <div className="hero-eyebrow">THREE SIGNALS · ONE TRANSPARENT VERDICT</div>
        <h1>
          Know exactly <span className="accent">why</span><br />
          a stock is flagged.
        </h1>
        <p className="hero-sub">
          MarketMind decouples Technicals, Fundamentals, and News Sentiment into
          readable sub-scores, combined with real SHAP explainability. Not a black box.
        </p>
        <a href="#analyzer" className="hero-cta">Run an analysis ↓</a>

        <div className="signal-strip">
          <div className="signal-chip"><span className="dot dot-technical" /> Technical <em>XGBoost + SHAP</em></div>
          <div className="signal-chip"><span className="dot dot-fundamental" /> Fundamental <em>Expert rules</em></div>
          <div className="signal-chip"><span className="dot dot-sentiment" /> Sentiment <em>FinBERT NLP</em></div>
        </div>

        <div className="stats-bar">
          <div className="stat-block">
            <strong>10</strong>
            <span>Large-cap tickers used for training</span>
          </div>
          <div className="stat-block">
            <strong>56%</strong>
            <span>Walk-forward validated accuracy</span>
          </div>
          <div className="stat-block">
            <strong>3</strong>
            <span>Independent, weighted signals</span>
          </div>
          <div className="stat-block">
            <strong>90d</strong>
            <span>Rolling price history per analysis</span>
          </div>
        </div>
      </header>

      {/* HOW IT WORKS */}
      <section className="how-it-works" id="how-it-works">
        <h2>How a verdict is built</h2>
        <div className="how-grid">
          <div className="how-card">
            <span className="dot dot-technical" />
            <h3>Technical</h3>
            <p>An XGBoost model trained on years of price history predicts direction. SHAP values expose exactly which indicator moved the needle.</p>
          </div>
          <div className="how-card">
            <span className="dot dot-fundamental" />
            <h3>Fundamental</h3>
            <p>P/E ratio and leverage are checked against sector benchmarks using transparent, auditable rules with no hidden weighting.</p>
          </div>
          <div className="how-card">
            <span className="dot dot-sentiment" />
            <h3>Sentiment</h3>
            <p>FinBERT, a finance-tuned language model, reads recent headlines the way analysts do, not the way generic sentiment tools do.</p>
          </div>
        </div>
      </section>

      {/* ANALYZER */}
      <section className="analyzer" id="analyzer">
        <h2>Try it live</h2>
        <p className="analyzer-sub">Enter any public ticker to see the full breakdown.</p>

        <div className="search-bar-wrap">
          <div className="market-toggle">
            <button
              className={`market-btn ${activeMarket === "US" ? "active" : ""}`}
              onClick={() => { setActiveMarket("US"); setTicker(""); setSuggestions([]); }}
            >US Markets</button>
            <button
              className={`market-btn ${activeMarket === "IN" ? "active" : ""}`}
              onClick={() => { setActiveMarket("IN"); setTicker(""); setSuggestions([]); }}
            >India (NSE / BSE)</button>
          </div>

          <div className="search-bar">
            <input
              type="text"
              placeholder={
                activeMarket === "IN"
                  ? "Search any Indian company: Zomato, Infosys, HDFC Bank"
                  : "Search by ticker or company name: AAPL, Amazon"
              }
              value={ticker}
              onChange={(e) => handleTickerInputChange(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
            />
            <button onClick={handleAnalyze} disabled={loading}>
              {loading ? "Analyzing…" : "Analyze"}
            </button>
          </div>

          {showSuggestions && (
            <div className="suggestions-dropdown">
              {suggestions.map((s, idx) => (
                <div
                  className="suggestion-item"
                  key={idx}
                  onMouseDown={() => selectSuggestion(s.symbol)}
                >
                  <span className="suggestion-symbol">{s.symbol}</span>
                  <span className="suggestion-name">{s.name}</span>
                  <span className="suggestion-region">{s.region}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {error && <p className="error">{error}</p>}
        {loading && <p className="loading">Fetching data, running models, generating explanation…</p>}

        {result && (
          <div className="dashboard">

            {/* RESULT HEADER */}
            <div className="result-header">
              <span className="rh-ticker">{result.ticker}</span>
              {result.is_indian && <span className="india-badge">NSE</span>}
              <span className="rh-name">{result.company_name || result.market}</span>
              <span className={`verdict-pill pill-${result.verdict.toLowerCase()}`}>{result.verdict}</span>
              <span className="rh-price">{currency}{result.latest_price?.toLocaleString("en-IN")}</span>
            </div>

            {/* TABS */}
            <div className="result-tabs">
              {RESULT_TABS.map(([key, label]) => (
                <button
                  key={key}
                  className={`result-tab ${activeTab === key ? "active" : ""}`}
                  onClick={() => setActiveTab(key)}
                >
                  {label}
                </button>
              ))}
            </div>

            {/* ===== OVERVIEW ===== */}
            {activeTab === "overview" && (
              <>
                <div className="dash-row">
                  <div className="panel snapshot-panel">
                    <div className="ticker-tag">{result.ticker}</div>
                    {result.company_name && <div className="snapshot-name">{result.company_name}</div>}
                    {result.sector && <div className="snapshot-sector">{result.sector}</div>}
                    {result.market && <div className="snapshot-market">{result.market}</div>}
                    <div className="snapshot-price">{currency}{result.latest_price?.toLocaleString("en-IN")}</div>
                    {priceChange !== null && (
                      <div className={`snapshot-change ${priceChange >= 0 ? "positive" : "negative"}`}>
                        {priceChange >= 0 ? "▲" : "▼"} {Math.abs(priceChange)}% <span>past 90d</span>
                      </div>
                    )}
                    <div className="snapshot-divider" />
                    {result.week52_low && result.week52_high && (
                      <div className="snapshot-row">
                        <span>52-Week Range</span>
                        <strong>{currency}{result.week52_low} – {currency}{result.week52_high}</strong>
                      </div>
                    )}
                    <div className="snapshot-row"><span>Investment Score</span><strong>{result.investment_score}</strong></div>
                    <div className="snapshot-row"><span>Risk Level</span><strong>{result.risk_level}</strong></div>

                    {user && (
                      inWatchlist ? (
                        <button className="wl-btn wl-btn-on" onClick={() => removeFromWatchlist(result.ticker)}>
                          On your watchlist (click to remove)
                        </button>
                      ) : (
                        <button className="wl-btn" onClick={addToWatchlist}>
                          Add to watchlist
                        </button>
                      )
                    )}
                  </div>

                  <div className="panel verdict-panel">
                    <h3>MarketMind Verdict</h3>
                    <VerdictDonut verdict={result.verdict} confidence={result.confidence_score} />
                    <p className="verdict-caption">
                      Based on {Object.values(result.breakdown).filter((v) => typeof v === "number").length} weighted signals
                    </p>

                    {result.trust_score && (
                      <div className="trust-badge">
                        <div className="trust-header">
                          <span>Data Completeness</span>
                          <strong>{result.trust_score.available}/{result.trust_score.total}</strong>
                        </div>
                        <div className="trust-bar-track">
                          <div
                            className={`trust-bar-fill ${
                              result.trust_score.percentage >= 80
                                ? "high"
                                : result.trust_score.percentage >= 60
                                ? "medium"
                                : "low"
                            }`}
                            style={{ width: `${result.trust_score.percentage}%` }}
                          />
                        </div>
                        <div className="trust-items">
                          {Object.entries(result.trust_score.breakdown).map(([label, ok]) => (
                            <span key={label} className={ok ? "trust-ok" : "trust-missing"}>
                              {label}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="panel chart-panel">
                    <h3>Price History <span className="card-tag">90 days</span></h3>
                    <ResponsiveContainer width="100%" height={230}>
                      <LineChart data={history}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#EDEFF3" />
                        <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#8891A7" }} minTickGap={40} />
                        <YAxis domain={["auto", "auto"]} tick={{ fontSize: 10, fill: "#8891A7" }} width={44} />
                        <Tooltip contentStyle={{ background: "#fff", border: "1px solid #E5E8EE", borderRadius: 8, fontFamily: "JetBrains Mono, monospace", fontSize: 12 }} />
                        <Line type="monotone" dataKey="close" stroke="#2563EB" dot={false} strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <SignalConflict data={result.signal_conflict} />

                <div className="panel">
                  <h3>Sub-Scores</h3>
                  <div className="score-cards">
                    {["technical", "fundamental", "sentiment"].map((key) => (
                      <div className="score-card" key={key}>
                        <div className="score-card-top">
                          <span className={`dot dot-${key}`} />
                          <span className="score-label">{key}</span>
                        </div>
                        <div className={`score-card-value ${result.breakdown[key] >= 0 ? "positive" : "negative"}`}>
                          {result.breakdown[key] > 0 ? "+" : ""}{Number(result.breakdown[key]).toFixed(2)}
                        </div>
                        <div className="score-bar-track">
                          <div
                            className={`score-bar-fill ${result.breakdown[key] >= 0 ? "positive" : "negative"}`}
                            style={{ width: `${Math.min(Math.abs(result.breakdown[key]) * 100, 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* ===== EXPLAINABILITY ===== */}
            {activeTab === "explain" && (
              <>
                <div className="panel">
                  <h3>Why this verdict?</h3>
                  <div className="explanation-columns">
                    {Object.entries(groupExplanation(result.explanation)).map(
                      ([category, reasons]) =>
                        reasons.length > 0 && (
                          <div className="explanation-group" key={category}>
                            <h4><span className={`dot dot-${category.toLowerCase()}`} />{category}</h4>
                            <ul>
                              {reasons.map((r, idx) => (
                                <li key={idx}>{r}</li>
                              ))}
                            </ul>
                          </div>
                        )
                    )}
                  </div>
                </div>

                {Array.isArray(result.counterfactuals) && (
                  <div className="panel">
                    <h3>What would change this verdict? <span className="card-tag">What-if</span></h3>
                    <p className="panel-note">
                      Computed on the technical model, holding fundamentals and sentiment fixed, at the default 40/30/30 weights.
                    </p>
                    {result.counterfactuals.length > 0 ? (
                      <ul className="cf-list">
                        {result.counterfactuals.map((c, idx) => (
                          <li key={idx}>
                            <span className={`cf-flip pill-${c.flips_to.toLowerCase()}`}>{c.flips_to}</span>
                            <div>
                              <div>{c.sentence}</div>
                              <small>Required move: {c.change_size_std} standard deviations of this indicator's history</small>
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="panel-note">
                        No single technical indicator change within a realistic range would flip this verdict. The fundamental and sentiment signals are anchoring it.
                      </p>
                    )}
                  </div>
                )}

                {Array.isArray(result.headline_attribution) && result.headline_attribution.length > 0 && (
                  <div className="panel">
                    <h3>Headlines behind the sentiment score</h3>
                    <p className="panel-note">
                      The individual headlines FinBERT read, ranked by how strongly they pushed the sentiment score.
                    </p>
                    <ul className="hl-list">
                      {result.headline_attribution.map((h, idx) => (
                        <li key={idx}>
                          <span className={`hl-pill hl-${h.label}`}>{h.label}</span>
                          <span className="hl-text">{h.headline}</span>
                          <span className="hl-conf">{(h.confidence * 100).toFixed(0)}%</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="panel">
                  <h3>Your Weighting <span className="card-tag">Adjust the formula</span></h3>
                  <p className="panel-note">
                    MarketMind combines the three sub-scores with a fixed 40/30/30 formula by default.
                    Change the weights to match your own investing style and see how the verdict responds.
                  </p>

                  <div className="preset-row">
                    {WEIGHT_PRESETS.map((p) => (
                      <button key={p.name} className="preset-btn" onClick={() => setWeights(p.weights)}>
                        {p.name}
                      </button>
                    ))}
                  </div>

                  <div className="weight-sliders">
                    {[
                      ["tech", "Technical", "technical"],
                      ["fund", "Fundamental", "fundamental"],
                      ["sent", "Sentiment", "sentiment"],
                    ].map(([key, label, dotKey]) => (
                      <div className="weight-row" key={key}>
                        <span className={`dot dot-${dotKey}`} />
                        <span className="weight-label">{label}</span>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={weights[key]}
                          onChange={(e) => setWeights({ ...weights, [key]: Number(e.target.value) })}
                        />
                        <span className="weight-value">
                          {custom ? `${(custom.weights[key] * 100).toFixed(0)}%` : "0%"}
                        </span>
                      </div>
                    ))}
                  </div>

                  {custom ? (
                    <div className="custom-result">
                      <div className="custom-col">
                        <span>MarketMind default (40/30/30)</span>
                        <strong style={{ color: VERDICT_COLOR[result.verdict] }}>{result.verdict}</strong>
                        <em>score {result.investment_score}</em>
                      </div>
                      <div className="custom-col">
                        <span>Your weighting</span>
                        <strong style={{ color: VERDICT_COLOR[custom.verdict] }}>{custom.verdict}</strong>
                        <em>score {custom.final.toFixed(3)} | confidence {(custom.confidence * 100).toFixed(0)}%</em>
                      </div>
                    </div>
                  ) : (
                    <p className="panel-note">Set at least one weight above zero.</p>
                  )}
                </div>
              </>
            )}

            {/* ===== FUNDAMENTALS ===== */}
            {activeTab === "fundamentals" && (
              <>
                <div className="panel">
                  <h3>Key Metrics</h3>
                  <div className="metrics-grid">
                    <div className="metric-item"><span>P/E (TTM)</span><strong>{result.pe_ratio ?? "—"}</strong></div>
                    <div className="metric-item"><span>P/B Ratio</span><strong>{result.pb_ratio ?? "—"}</strong></div>
                    <div className="metric-item"><span>EPS</span><strong>{result.eps ? `${currency}${result.eps}` : "—"}</strong></div>
                    <div className="metric-item"><span>PEG Ratio</span><strong>{result.peg_ratio ?? "—"}</strong></div>
                    <div className="metric-item"><span>Profit Margin</span><strong>{result.profit_margin ? `${(result.profit_margin * 100).toFixed(1)}%` : "—"}</strong></div>
                    <div className="metric-item"><span>Dividend Yield</span><strong>{result.dividend_yield ? `${(result.dividend_yield * 100).toFixed(2)}%` : "—"}</strong></div>
                  </div>
                </div>

                {result.description && (
                  <div className="panel">
                    <h3>Company Profile</h3>
                    <p className="company-description">
                      {descExpanded ? result.description : `${result.description.slice(0, 320)}...`}
                      <span className="read-more" onClick={() => setDescExpanded(!descExpanded)}>
                        {descExpanded ? " Show less" : " Read more"}
                      </span>
                    </p>
                  </div>
                )}

                {peersData && peersData.length > 0 && (
                  <div className="panel">
                    <h3>Peers</h3>
                    <div className="peers-grid">
                      {peersData.map((p, idx) => (
                        <div className="peer-card" key={idx}>
                          <div className="peer-name">{p.company_name}</div>
                          <div className="peer-ticker">{p.ticker}</div>
                          <div className="peer-stats">
                            <div><span>P/E Ratio</span><strong>{p.pe_ratio ?? "—"}</strong></div>
                            <div>
                              <span>1Y Return</span>
                              <strong className={p.one_year_return_pct >= 0 ? "positive" : "negative"}>
                                {p.one_year_return_pct >= 0 ? "+" : ""}{p.one_year_return_pct}%
                              </strong>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {financialsData && financialsData.length > 0 && (
                  <div className="panel">
                    <h3>Financials <span className="card-tag">Quarterly, {currency}M</span></h3>
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={financialsData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#EDEFF3" />
                        <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#8891A7" }} />
                        <YAxis tick={{ fontSize: 10, fill: "#8891A7" }} />
                        <Tooltip contentStyle={{ background: "#fff", border: "1px solid #E5E8EE", borderRadius: 8, fontFamily: "JetBrains Mono, monospace", fontSize: 12 }} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Bar dataKey="revenue_millions" name="Revenue" fill="#2563EB" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="net_income_millions" name="Net Income" fill="#0F9D6E" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </>
            )}

            {/* ===== RISK ===== */}
            {activeTab === "risk" && (
              <>
                <StressTestPanel ticker={result.ticker} />
                <CalibrationPanel probability={result.technical_probability} />
              </>
            )}
          </div>
        )}
      </section>

      {/* PORTFOLIO ADVISOR */}
      <section className="advisor-section" id="advisor">
        <h2>Diversify your portfolio</h2>
        <p className="analyzer-sub">
          One top historical performer per sector, built from a diversified basket plus your own search history.
        </p>

        {!advisorData && (
          <div style={{ textAlign: "center" }}>
            <button className="hero-cta" onClick={fetchAdvisor} disabled={advisorLoading}>
              {advisorLoading ? "Analyzing sectors…" : "Get recommendations"}
            </button>
          </div>
        )}

        {advisorData && (
          <div className="advisor-grid">
            {advisorData.recommendations.map((r, idx) => (
              <div className="advisor-card" key={idx}>
                <div className="advisor-sector">{r.sector}</div>
                <div className="advisor-ticker">{r.ticker}</div>
                <div className="advisor-stats">
                  <div><span>1Y Return</span><strong className="positive">+{r.total_return_pct}%</strong></div>
                  <div><span>Volatility</span><strong>{r.volatility_pct}%</strong></div>
                  <div><span>Risk-Adj Score</span><strong>{r.risk_adjusted_score}</strong></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* TRACK RECORD */}
      <section className="track-section" id="track-record">
        <h2>Track record</h2>
        <p className="analyzer-sub">
          How the technical signal would have performed on data the model never saw during training.
        </p>

        {!trackRecord && (
          <div style={{ textAlign: "center" }}>
            <button className="hero-cta" onClick={() => fetchTrackRecord(false)} disabled={trackLoading}>
              {trackLoading ? "Running backtest…" : "Run the backtest"}
            </button>
            {trackLoading && (
              <p className="loading">
                This downloads 10 years of prices and trains a fresh model. The first run can take a minute or two.
              </p>
            )}
          </div>
        )}

        {trackError && <p className="error">{trackError}</p>}

        {trackRecord && trackRecord.available === false && (
          <p className="error">{trackRecord.note}</p>
        )}

        {trackRecord && trackRecord.available !== false && (
          <div className="track-body">
            <div className="track-stats">
              <div className="track-stat">
                <span>Test period</span>
                <strong>{trackRecord.test_start}</strong>
                <em>to {trackRecord.test_end}</em>
              </div>
              <div className="track-stat">
                <span>Buy signals</span>
                <strong>{trackRecord.signals.buy}</strong>
                <em>{trackRecord.signals.avoid} Avoid, {trackRecord.signals.hold} Hold</em>
              </div>
              <div className="track-stat">
                <span>Buy hit rate</span>
                <strong>{trackRecord.buy_hit_rate_pct === null ? "n/a" : `${trackRecord.buy_hit_rate_pct}%`}</strong>
                <em>vs {trackRecord.baseline_up_rate_pct}% of all periods rising</em>
              </div>
              <div className="track-stat">
                <span>Avg 5-day return after Buy</span>
                <strong>{fmtPct(trackRecord.avg_return_after_buy_pct)}</strong>
                <em>after Avoid {fmtPct(trackRecord.avg_return_after_avoid_pct)} | all {fmtPct(trackRecord.avg_return_all_pct)}</em>
              </div>
              <div className="track-stat">
                <span>Signal strategy</span>
                <strong>{fmtPct(trackRecord.strategy_total_return_pct)}</strong>
                <em>total return over the period</em>
              </div>
              <div className="track-stat">
                <span>Buy and hold</span>
                <strong>{fmtPct(trackRecord.buy_hold_total_return_pct)}</strong>
                <em>same basket, same period</em>
              </div>
            </div>

            <div className="panel">
              <h3>Growth of 100 <span className="card-tag">{trackRecord.n_tickers} stocks, 5-day holds</span></h3>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={trackRecord.equity_curve}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#EDEFF3" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#8891A7" }} minTickGap={50} />
                  <YAxis domain={["auto", "auto"]} tick={{ fontSize: 10, fill: "#8891A7" }} width={44} />
                  <Tooltip contentStyle={{ background: "#fff", border: "1px solid #E5E8EE", borderRadius: 8, fontFamily: "JetBrains Mono, monospace", fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Line type="monotone" dataKey="strategy" name="MarketMind technical signal" stroke="#2563EB" dot={false} strokeWidth={2} />
                  <Line type="monotone" dataKey="buy_hold" name="Buy and hold" stroke="#8891A7" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="panel">
              <h3>How to read this</h3>
              <ul className="track-notes">
                {trackRecord.notes.map((n, idx) => (
                  <li key={idx}>{n}</li>
                ))}
              </ul>
              <button
                className="preset-btn"
                onClick={() => fetchTrackRecord(true)}
                disabled={trackLoading}
              >
                {trackLoading ? "Re-running…" : "Re-run with fresh data"}
              </button>
            </div>
          </div>
        )}
      </section>

      <footer className="footer">
        <Logo />
        <p>MarketMind is a decision-support tool, not financial advice. Predictions are probabilistic, not guarantees.</p>
      </footer>

      <ChatBot stockContext={result ? {
        ticker: result.ticker,
        verdict: result.verdict,
        investment_score: result.investment_score,
        confidence_score: result.confidence_score,
        risk_level: result.risk_level,
        explanation: result.explanation,
        is_indian: result.is_indian,
        currency_symbol: result.currency_symbol,
      } : null} />
    </div>
  );
}

export default App;