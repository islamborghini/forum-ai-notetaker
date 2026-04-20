import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { uploadSession, getCourses } from "../api/backend";

const ALLOWED_EXTENSIONS = ["mp4", "mp3", "wav", "m4a"];

export default function Upload() {
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [courseId, setCourseId] = useState("");
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getCourses()
      .then((payload) => {
        if (cancelled) return;
        const eligible = (payload.data || []).filter(
          (c) => c.role === "instructor" || c.role === "ta"
        );
        setCourses(eligible);
        if (eligible.length === 1) {
          setCourseId(String(eligible[0].id));
        }
      })
      .catch((err) => {
        if (cancelled) return;
        setLoadError(err.message || "Could not load your courses. Please refresh the page.");
      })
      .finally(() => {
        if (!cancelled) setLoadingCourses(false);
      });
    return () => { cancelled = true; };
  }, []);

  function isAllowedFile(candidateFile) {
    if (!candidateFile?.name) return false;
    const ext = candidateFile.name.split(".").pop()?.toLowerCase();
    return ALLOWED_EXTENSIONS.includes(ext);
  }

  function handlePickedFile(candidateFile) {
    if (!candidateFile) return;
    if (!isAllowedFile(candidateFile)) {
      setError("Unsupported file type. Use mp4, mp3, wav, or m4a.");
      return;
    }
    setError("");
    setFile(candidateFile);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (loading) return;
    setMessage("");
    setError("");

    if (!courseId) {
      setError("Please select a course.");
      return;
    }
    if (!title.trim()) {
      setError("Title is required.");
      return;
    }
    if (!file) {
      setError("Please select a file.");
      return;
    }

    setLoading(true);
    try {
      const payload = await uploadSession({
        title: title.trim(),
        file,
        courseId,
      });
      setMessage(payload.message || "Upload successful.");
      setTitle("");
      setFile(null);
    } catch (err) {
      setError(err.message || "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  if (loadingCourses) {
    return (
      <div className="container">
        <p>Loading...</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="container">
        <h1>Upload Session</h1>
        <p className="error-text" role="alert">{loadError}</p>
      </div>
    );
  }

  if (courses.length === 0) {
    return (
      <div className="container">
        <h1>Upload Session</h1>
        <div className="empty-state">
          <p>
            You need to be an instructor or TA in a course to upload sessions.
          </p>
          <div className="empty-state-actions">
            <Link to="/courses/create" className="btn-link">
              Create a course
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Upload Session</h1>

      <form className="upload-form" onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="course">Course</label>
          <select
            id="course"
            value={courseId}
            onChange={(e) => setCourseId(e.target.value)}
            disabled={loading}
          >
            <option value="">Select a course</option>
            {courses.map((c) => (
              <option key={c.id} value={String(c.id)}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-field">
          <label htmlFor="title">Title</label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Class recording title"
            disabled={loading}
          />
        </div>

        <div
          className={`upload-dropzone ${isDragOver ? "drag-over" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragOver(false);
            handlePickedFile(e.dataTransfer.files?.[0]);
          }}
        >
          <label htmlFor="file">Recording</label>
          <input
            id="file"
            type="file"
            accept=".mp4,.mp3,.wav,.m4a"
            onChange={(e) => handlePickedFile(e.target.files?.[0])}
            disabled={loading}
          />

          <p className="muted-text">Drag and drop a file here or choose one.</p>
          <p className="muted-text">Allowed: mp4, mp3, wav, m4a</p>
        </div>

        {file ? <p className="muted-text">Selected file: {file.name}</p> : null}

        <button type="submit" disabled={loading}>
          {loading ? "Uploading..." : "Upload"}
        </button>
      </form>

      {message ? <p className="success-text" role="status">{message}</p> : null}
      {error ? <p className="error-text" role="alert">{error}</p> : null}
    </div>
  );
}
