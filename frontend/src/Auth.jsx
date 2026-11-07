import { useState } from "react";
import axios from "axios";

export default function AuthModal({ onClose, onAuthSuccess }) {
  const [mode, setMode] = useState("login"); // "login" or "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const endpoint = mode === "login" ? "login" : "signup";
      const res = await axios.post(`http://127.0.0.1:8000/auth/${endpoint}`, {
        email,
        password,
      });
      localStorage.setItem("mm_token", res.data.access_token);
      localStorage.setItem("mm_email", email);
      onAuthSuccess(email, res.data.access_token);
      onClose();
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        // Pydantic validation error — extract readable message
        const raw = detail[0]?.msg || "Invalid input";
        // Strip Pydantic's "Value error, " prefix if present
        setError(raw.replace(/^Value error,\s*/i, ""));
      } else if (typeof detail === "string") {
        setError(detail);
      } else if (!err.response) {
        setError("Cannot connect to server. Is the backend running?");
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <button className="auth-close" onClick={onClose}>×</button>

        <h2>{mode === "login" ? "Welcome back" : "Create your account"}</h2>
        <p className="auth-sub">
          {mode === "login"
            ? "Log in to see your search history."
            : "Sign up to track the stocks you analyze."}
        </p>

        <form onSubmit={handleSubmit}>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={mode === "signup" ? "Min 8 chars, 1 uppercase, 1 number" : "••••••••"}
            required
          />
          {mode === "signup" && (
            <p style={{ fontSize: "11px", color: "#8891A7", margin: "4px 0 0", lineHeight: 1.4 }}>
              Password must be <strong>8+ characters</strong> with at least one <strong>uppercase letter</strong> and one <strong>number</strong>.
            </p>
          )}

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Please wait…" : mode === "login" ? "Log In" : "Sign Up"}
          </button>
        </form>

        <p className="auth-switch">
          {mode === "login" ? (
            <>Don't have an account? <span onClick={() => { setMode("signup"); setError(null); }}>Sign up</span></>
          ) : (
            <>Already have an account? <span onClick={() => { setMode("login"); setError(null); }}>Log in</span></>
          )}
        </p>
      </div>
    </div>
  );
}