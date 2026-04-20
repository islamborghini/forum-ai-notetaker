import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getCourses, getSessions } from "../api/backend";
import useAuth from "../hooks/useAuth";
import {
  getSessionStatusLabel,
  SESSION_STATUS_FILTERS,
} from "../utils/sessionStatus";

export default function Dashboard() {
  const { user } = useAuth();
  const isProfessor = user?.user_type === "professor";
  const [courses, setCourses] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [coursesError, setCoursesError] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError("");
      try {
        const results = await Promise.allSettled([
          getCourses(),
          getSessions(),
        ]);

        if (results[0].status === "fulfilled") {
          setCourses(results[0].value.data || []);
        } else {
          setCoursesError("Could not load courses.");
        }
        if (results[1].status === "fulfilled") {
          setSessions(results[1].value.data || []);
        }

        const failures = results.filter((r) => r.status === "rejected");
        if (failures.length === results.length) {
          setError("Failed to load data.");
        }
      } catch (err) {
        setError(err.message || "Failed to load data.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const summary = useMemo(() => {
    const total = sessions.length;
    const ready = sessions.filter(
      (s) => s.status === "transcribed" || s.status === "notes_generated"
    ).length;
    const failed = sessions.filter((s) => s.status === "failed").length;
    return { total, ready, failed };
  }, [sessions]);

  const filteredSessions = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();
    return sessions.filter((s) => {
      const statusMatch =
        statusFilter === "all" ? true : s.status === statusFilter;
      const title = (s.title || "").toLowerCase();
      const filename = (s.original_filename || "").toLowerCase();
      const queryMatch = !query || title.includes(query) || filename.includes(query);
      return statusMatch && queryMatch;
    });
  }, [sessions, statusFilter, searchTerm]);

  if (loading) {
    return (
      <div className="container">
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <p className="error-text" role="alert">{error}</p>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
      </div>

      <h2 className="section-heading">Your courses</h2>

      {coursesError ? (
        <p className="error-text" role="alert">{coursesError}</p>
      ) : courses.length === 0 ? (
        <div className="empty-state">
          <p>You are not in any courses yet.</p>
          <div className="empty-state-actions">
            {isProfessor ? (
              <Link to="/courses/create" className="btn-link">Create a course</Link>
            ) : (
              <Link to="/courses/join" className="btn-link">Join a course</Link>
            )}
          </div>
        </div>
      ) : (
        <div className="course-grid">
          {courses.map((course) => (
            <Link
              to={`/courses/${course.id}`}
              key={course.id}
              className="course-card"
            >
              <div className="course-card-name">{course.name}</div>
              <div className="course-card-meta">
                <span className={`role-badge role-badge--${course.role || "student"}`}>
                  {course.role}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}

      <h2 className="section-heading">All sessions</h2>

      <div className="dashboard-stats">
        <div className="stat-card">
          <span>Total sessions</span>
          <strong>{summary.total}</strong>
        </div>
        <div className="stat-card">
          <span>Ready</span>
          <strong>{summary.ready}</strong>
        </div>
        <div className="stat-card">
          <span>Failed</span>
          <strong>{summary.failed}</strong>
        </div>
      </div>

      <div className="dashboard-toolbar">
        <input
          type="text"
          placeholder="Search title or filename"
          aria-label="Search sessions"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          aria-label="Filter by status"
        >
          <option value="all">All statuses</option>
          {SESSION_STATUS_FILTERS.map((statusOption) => (
            <option key={statusOption.value} value={statusOption.value}>
              {statusOption.label}
            </option>
          ))}
        </select>
      </div>

      {filteredSessions.length === 0 ? (
        <p className="muted-text">No sessions yet. Upload one to get started.</p>
      ) : (
        <ul className="session-list">
          {filteredSessions.map((session) => (
            <li className="session-card" key={session.id}>
              <div>
                <strong>{session.title}</strong>
                <p className="muted-text">{session.original_filename}</p>
                <p className="muted-text">
                  Status: {getSessionStatusLabel(session.status)}
                </p>
              </div>
              <Link to={`/notes/${session.id}`}>View transcript/notes</Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
