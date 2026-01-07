import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

function AdminLogin() {
  const { login, error, loading } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleLogin = async () => {
    setSubmitting(true);
    try {
      const u = await login(email, password);
      if (u?.role === "ADMIN") {
        navigate("/admin/performance", { replace: true });
      } else {
        navigate("/", { replace: true });
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-card">
        <h2 className="auth-title">Welcome Back!</h2>
        <p className="auth-subtitle">We missed you! Please enter your details</p>

        {error && (
          <div style={{ color: "crimson", marginBottom: 10 }}>
            {error}
          </div>
        )}

        <label className="auth-label">Email</label>
        <input
          className="auth-input"
          placeholder="Enter your Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label className="auth-label">Password</label>
        <div className="password-wrapper">
          <input
            className="auth-input"
            type={showPassword ? "text" : "password"}
            placeholder="Enter Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button
            type="button"
            className="eye-btn"
            onClick={() => setShowPassword((v) => !v)}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? "🙈" : "👁"}
          </button>
        </div>

        <button
          className="auth-button"
          onClick={handleLogin}
          disabled={submitting || loading}
        >
          {submitting ? "Signing in..." : "Sign in"}
        </button>
      </div>
    </main>
  );
}

export default AdminLogin;
