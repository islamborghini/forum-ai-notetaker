import { Link } from "react-router-dom";
import useAuth from "../hooks/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav>
      <div className="nav-links">
        {user ? (
          <>
            <Link to="/">Dashboard</Link>
            <Link to="/upload">Upload</Link>
            <Link to="/search">Search</Link>
          </>
        ) : (
          <Link to="/login">Forum AI Notetaker</Link>
        )}
      </div>

      <div className="nav-user">
        {user ? (
          <>
            <span className="nav-greeting">
              Hey, {user.name || user.email}
            </span>
            <button className="nav-logout" onClick={logout}>
              Log out
            </button>
          </>
        ) : (
          <Link to="/login">Log in</Link>
        )}
      </div>
    </nav>
  );
}
