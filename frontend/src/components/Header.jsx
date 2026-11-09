import { NavLink } from "react-router-dom";

function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo">
          <div className="logo-circle">cm</div>
          <span>Classroom monitoring</span>
        </div>

        <nav className="nav">
          <NavLink to="/" end className="nav-btn">
            Home
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default Header;
