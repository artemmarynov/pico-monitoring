import { useNavigate, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function AdminHome() {
  const { isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  if (!isAdmin) {
    return <Navigate to="/admin/login" replace />;
  }

  const handleExit = () => {
    logout();
    navigate("/admin/login");
  };

  return (
    <main className="admin-page">
      <aside className="admin-sidebar">
        <img
          className="admin-avatar"
          src="/assets/avatar.jpg"
          alt="Admin avatar"
        />

        <h3>Hello Martin!</h3>

        <button className="exit-btn" onClick={handleExit}>
          Exit
        </button>

        <button className="menu-btn primary">Models</button>
        <button className="menu-btn secondary">Performance</button>
        <button className="menu-btn tertiary">Risk</button>
      </aside>

      <section className="admin-content">
        <h2 className="dashboard-title">Website traffic schedule</h2>

        <img
          className="dashboard-image"
          src="/assets/chart.png"
          alt="Website traffic chart"
        />
      </section>
    </main>
  );
}

export default AdminHome;
