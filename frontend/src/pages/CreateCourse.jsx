import { useState, useRef, useEffect } from "react";
import { Link, Navigate } from "react-router-dom";
import { createCourse } from "../api/backend";
import useAuth from "../hooks/useAuth";

export default function CreateCourse() {
  const { user } = useAuth();
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [createdCourse, setCreatedCourse] = useState(null);
  const [copied, setCopied] = useState(false);
  const timerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  if (user && user.user_type !== "professor") {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (loading) return;
    setError("");

    if (!name.trim()) {
      setError("Course name is required.");
      return;
    }

    setLoading(true);
    try {
      const payload = await createCourse(name.trim());
      setCreatedCourse(payload.data);
    } catch (err) {
      setError(err.message || "Failed to create course.");
    } finally {
      setLoading(false);
    }
  }

  function handleCopy() {
    if (!createdCourse) return;
    navigator.clipboard.writeText(createdCourse.invite_code).catch(() => {});
    setCopied(true);
    timerRef.current = setTimeout(() => setCopied(false), 2000);
  }

  if (createdCourse) {
    return (
      <div className="auth-page">
        <div className="auth-card course-success-card">
          <h1>Course created</h1>
          <p className="muted-text">{createdCourse.name}</p>

          <p className="invite-code-label">
            Share this invite code with your students:
          </p>

          <div className="invite-code-display" aria-label="Invite code">
            {createdCourse.invite_code}
          </div>

          <button
            className="btn-secondary invite-code-copy"
            onClick={handleCopy}
            aria-live="polite"
          >
            {copied ? "Copied!" : "Copy code"}
          </button>

          <p className="course-success-link">
            <Link to="/">Go to Dashboard</Link>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Create course</h1>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="course-name">Course name</label>
            <input
              id="course-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. CS 101 — Intro to Computer Science"
              disabled={loading}
              autoComplete="off"
            />
          </div>

          {error ? <p className="error-text" role="alert">{error}</p> : null}

          <button type="submit" disabled={loading}>
            {loading ? "Creating..." : "Create course"}
          </button>
        </form>
      </div>
    </div>
  );
}
