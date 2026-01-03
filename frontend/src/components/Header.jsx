import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Header({ onHomeClick }) {
  const { isAdmin } = useAuth();

  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo">
          <div className="logo-circle">df</div>
          <span>deepfake.ai</span>
        </div>

        <nav className="nav">
          {isAdmin && (
            <NavLink
              to="/admin/performance"
              className="nav-btn"
              onClick={onHomeClick}
            >
              Home
            </NavLink>
          )}

          <NavLink to="/about" className="nav-btn">
            About us
          </NavLink>

          <NavLink to="/contacts" className="nav-btn">
            Contacts
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default Header;
