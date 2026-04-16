import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getCourse, getCourseSessions, updateMemberRole } from "../api/backend";

export default function Course() {
  const { id } = useParams();
  const [course, setCourse] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [promoteError, setPromoteError] = useState("");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError("");
      try {
        const results = await Promise.allSettled([
          getCourse(id),
          getCourseSessions(id),
        ]);

        if (results[0].status === "fulfilled") {
          setCourse(results[0].value.data);
        } else {
          setError(results[0].reason?.message || "Failed to load course.");
        }

        if (results[1].status === "fulfilled") {
          setSessions(results[1].value.data || []);
        }
      } catch (err) {
        setError(err.message || "Failed to load course.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  async function handlePromote(userId, userName) {
    setPromoteError("");
    const prevMembers = course.members.map((m) => ({ ...m }));

    setCourse((prev) => ({
      ...prev,
      members: prev.members.map((m) =>
        m.user_id === userId ? { ...m, role: "ta" } : m
      ),
    }));

    try {
      await updateMemberRole(id, userId, "ta");
    } catch (err) {
      setCourse((prev) => ({ ...prev, members: prevMembers }));
      setPromoteError(`Failed to promote ${userName}: ${err.message}`);
    }
  }

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

  if (!course) return null;

  const isInstructor = course.your_role === "instructor";
  const canSeeCode = course.your_role === "instructor" || course.your_role === "ta";

  return (
    <div className="container">
      <div className="course-header">
        <h1>{course.name}</h1>
        <span className={`role-badge role-badge--${course.your_role || "student"}`}>
          {course.your_role}
        </span>
      </div>

      {canSeeCode && course.invite_code ? (
        <div className="course-invite-section">
          <p className="muted-text">Invite code</p>
          <div className="invite-code-display">{course.invite_code}</div>
        </div>
      ) : null}

      <h2 className="section-heading">
        Members ({course.members ? course.members.length : 0})
      </h2>

      {promoteError ? (
        <p className="error-text" role="alert">{promoteError}</p>
      ) : null}

      <ul className="member-list">
        {(course.members || []).map((member) => (
          <li className="member-row" key={member.user_id}>
            <div className="member-info">
              <span className="member-name">{member.name}</span>
              <span className={`role-badge role-badge--${member.role || "student"}`}>
                {member.role}
              </span>
            </div>
            {isInstructor && member.role === "student" ? (
              <button
                className="btn-secondary btn-small"
                onClick={() => handlePromote(member.user_id, member.name)}
                aria-label={`Promote ${member.name} to TA`}
              >
                Promote to TA
              </button>
            ) : null}
          </li>
        ))}
      </ul>

      <h2 className="section-heading">
        Sessions ({sessions.length})
      </h2>

      {sessions.length === 0 ? (
        <p className="muted-text">
          No sessions in this course yet.{" "}
          <Link to="/upload">Upload one</Link>
        </p>
      ) : (
        <ul className="session-list">
          {sessions.map((session) => (
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
      )}
    </div>
  );
}
