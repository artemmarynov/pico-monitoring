import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function AdminSidebar() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleExit = () => {
    logout();
    navigate("/");
  };

  return (
    <aside className="admin-sidebar">
      <img
        src="../../public/admin_picture.png"
        alt="Admin avatar"
        className="admin-avatar"
        onClick={() => navigate("/admin")}
      />

      <h3>Hello Admin!</h3>

      <button className="exit-btn" onClick={handleExit}>
        Exit
      </button>

      <NavLink
        to="/admin/performance"
        className={({ isActive }) =>
          `menu-btn ${isActive ? "active" : ""}`
        }
      >
        Performance
      </NavLink>

      <NavLink
        to="/admin/misc"
        className={({ isActive }) =>
          `menu-btn ${isActive ? "active" : ""}`
        }
      >
        Misс
      </NavLink>
    </aside>
  );
}

export default AdminSidebar;
