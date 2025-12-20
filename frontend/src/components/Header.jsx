import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Header() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleAdminClick = () => {
    if (isAuthenticated) {
      navigate("/admin");
    } else {
      navigate("/admin/login");
    }
  };

  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo">
          <div className="logo-circle">df</div>
          <span>deepfake.ai</span>
        </div>

        <nav className="nav">
          <NavLink to="/" className="nav-btn">Home</NavLink>
          <NavLink to="/about" className="nav-btn">About us</NavLink>
          <NavLink to="/contacts" className="nav-btn">Contacts</NavLink>
          <NavLink to="/admin" className="nav-btn">Admin dashboard</NavLink>
        </nav>
      </div>
    </header>
  );
}

export default Header;
