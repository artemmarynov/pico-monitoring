import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

function AdminLogin() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = () => {
    login();
    navigate("/admin/performance");
  };

  return (
    <main className="auth-page">
      <div className="auth-card">
        <h2 className="auth-title">Welcome Back!</h2>
        <p className="auth-subtitle">
          We missed you! Please enter your details
        </p>

        <label className="auth-label">Email</label>
        <input className="auth-input" placeholder="Enter your Email" />

        <label className="auth-label">Password</label>
        <div className="password-wrapper">
          <input
            className="auth-input"
            type="password"
            placeholder="Enter Password"
          />
          <span className="eye-icon">👁</span>
        </div>

        <a className="forgot-link">Forgot password?</a>

        <button className="auth-button" onClick={handleLogin}>
          Sign in
        </button>
      </div>
    </main>
  );
}
export default AdminLogin;
