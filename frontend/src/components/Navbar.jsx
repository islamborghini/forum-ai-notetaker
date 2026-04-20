import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import { getCourses } from "../api/backend";

export default function Navbar() {
  const { user, logout } = useAuth();
  const isProfessor = user?.user_type === "professor";
  const [isTaSomewhere, setIsTaSomewhere] = useState(false);
  const canUpload = Boolean(user) && (isProfessor || isTaSomewhere);

  useEffect(() => {
    if (!user || isProfessor) return;
    let cancelled = false;
    getCourses()
      .then((payload) => {
        if (cancelled) return;
        const eligible = (payload.data || []).some(
          (c) => c.role === "instructor" || c.role === "ta"
        );
        setIsTaSomewhere(eligible);
      })
      .catch(() => {
        if (!cancelled) setIsTaSomewhere(false);
      });
    return () => { cancelled = true; };
  }, [user, isProfessor]);

  return (
    <nav>
      <div className="nav-links">
        {user ? (
          <>
            <Link to="/">Dashboard</Link>
            {isProfessor ? (
              <Link to="/courses/create">Create Course</Link>
            ) : (
              <Link to="/courses/join">Join Course</Link>
            )}
            {canUpload ? <Link to="/upload">Upload</Link> : null}
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
