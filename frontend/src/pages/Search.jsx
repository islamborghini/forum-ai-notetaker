import { useState } from "react";
import { Link } from "react-router-dom";
import { searchSessions } from "../api/backend";

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedQuery = query.trim();
    setHasSearched(true);
    setError("");

    if (!trimmedQuery) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const payload = await searchSessions(trimmedQuery);
      setResults(payload.data || []);
    } catch (err) {
      setError(err.message || "Search failed.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>Search sessions</h1>
      <p className="muted-text">
        Find recordings by session title or transcript content.
      </p>

      <form className="search-form" onSubmit={handleSubmit}>
        <input
          type="search"
          placeholder="Search title or transcript"
          aria-label="Search title or transcript"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error ? (
        <p className="error-text" role="alert">{error}</p>
      ) : null}

      {hasSearched && !loading && !error && results.length === 0 ? (
        <p className="muted-text">No matching sessions found.</p>
      ) : null}

      {results.length > 0 ? (
        <ul className="session-list">
          {results.map((session) => (
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
