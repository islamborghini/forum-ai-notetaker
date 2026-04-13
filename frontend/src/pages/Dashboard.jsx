import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getSessions } from "../api/backend";

export default function Dashboard() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  async function loadSessions() {
    setLoading(true);
    setError("");

    try {
      const payload = await getSessions();
      // Backend wraps rows inside payload.data.
      setSessions(payload.data || []);
    } catch (err) {
      setError(err.message || "Failed to load sessions.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // Load sessions once when this page mounts.
    loadSessions();
  }, []);

  const summary = useMemo(() => {
    const total = sessions.length;
    const transcribed = sessions.filter(
      (session) => session.status === "transcribed"
    ).length;
    const failed = sessions.filter((session) => session.status === "failed").length;

    return { total, transcribed, failed };
  }, [sessions]);

  const filteredSessions = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return sessions.filter((session) => {
      const statusMatch =
        statusFilter === "all" ? true : session.status === statusFilter;

      const title = (session.title || "").toLowerCase();
      const filename = (session.original_filename || "").toLowerCase();
      const queryMatch = !query || title.includes(query) || filename.includes(query);

      return statusMatch && queryMatch;
    });
  }, [sessions, statusFilter, searchTerm]);

  return (
    <div className="container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button onClick={loadSessions} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <span>Total sessions</span>
          <strong>{summary.total}</strong>
        </div>
        <div className="stat-card">
          <span>Transcribed</span>
          <strong>{summary.transcribed}</strong>
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
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
        />

        <select
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
        >
          <option value="all">All statuses</option>
          <option value="uploaded">Uploaded</option>
          <option value="processing">Processing</option>
          <option value="transcribed">Transcribed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {loading ? <p>Loading sessions...</p> : null}
      {error ? <p className="error-text">{error}</p> : null}

      {!loading && !error && filteredSessions.length === 0 ? (
        <p>No sessions yet. Upload one to get started.</p>
      ) : null}

      {!loading && !error && filteredSessions.length > 0 ? (
        <ul className="session-list">
          {filteredSessions.map((session) => (
            <li className="session-card" key={session.id}>
              <div>
                <strong>{session.title}</strong>
                <p className="muted-text">{session.original_filename}</p>
                <p className="muted-text">Status: {session.status}</p>
              </div>

              <Link to={`/notes/${session.id}`}>View transcript/notes</Link>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
