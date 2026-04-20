import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { joinCourse } from "../api/backend";
import useAuth from "../hooks/useAuth";

export default function JoinCourse() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (user && user.user_type !== "student") {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (loading) return;
    setError("");

    if (!code.trim()) {
      setError("Invite code is required.");
      return;
    }

    setLoading(true);
    try {
      await joinCourse(code.trim());
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message || "Failed to join course.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Join course</h1>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="invite-code">Invite code</label>
            <input
              id="invite-code"
              type="text"
              className="invite-code-input"
              value={code}
              onChange={(e) => {
                setCode(e.target.value.toUpperCase());
                setError("");
              }}
              placeholder="e.g. A1B2C3D4E5F6"
              disabled={loading}
              autoComplete="off"
            />
          </div>

          {error ? <p className="error-text" role="alert">{error}</p> : null}

          <button type="submit" disabled={loading}>
            {loading ? "Joining..." : "Join course"}
          </button>
        </form>
      </div>
    </div>
  );
}
