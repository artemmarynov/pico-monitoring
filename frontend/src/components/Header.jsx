import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Header() {
  const { isAdmin } = useAuth();

  const homePath = isAdmin ? "/admin/performance" : "/admin/login";

  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo">
          <div className="logo-circle">cm</div>
          <span>Classroom monitoring</span>
        </div>

        <nav className="nav">
          <NavLink to={homePath} className="nav-btn">
            Home
          </NavLink>

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
