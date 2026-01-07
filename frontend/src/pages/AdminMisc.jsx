import { useState } from "react";
import { apiCreateAdmin } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function AdminMisc() {
  const { isAdmin } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);

  const onCreate = async (e) => {
    e?.preventDefault?.();

    setMsg(null);
    setErr(null);
    setLoading(true);

    try {
      await apiCreateAdmin(email, password);
      setMsg("New admin created successfully.");
      setEmail("");
      setPassword("");
    } catch (e2) {
      setErr(e2?.message || "Failed to create admin");
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="misc-page">
        <div className="card misc-card">
          <h2 className="misc-title">Admin access required</h2>
          <p className="misc-subtitle">Please sign in with an ADMIN account.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="misc-page">
      <div className="card misc-card">
        <div className="card-head">
          <h2 className="card-title">CREATE NEW ADMIN</h2>
          <div className="card-rule" />
        </div>

        {msg && <div className="alert alert-success">{msg}</div>}
        {err && <div className="alert alert-error">{err}</div>}

        <form className="form misc-form" onSubmit={onCreate}>
          <label className="field">
            <span className="field-label">EMAIL</span>
            <input
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="newadmin@example.com"
              autoComplete="email"
              required
            />
          </label>

          <label className="field">
            <span className="field-label">PASSWORD</span>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="StrongPassword123!"
              autoComplete="new-password"
              required
            />
          </label>

          <button
            className="btn btn-primary"
            type="submit"
            disabled={loading || !email || !password}
          >
            {loading ? "CREATING..." : "CREATE ADMIN"}
          </button>
        </form>
      </div>
    </div>
  );
}
