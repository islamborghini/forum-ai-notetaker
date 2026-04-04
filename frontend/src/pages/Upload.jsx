import { useState } from "react";
import { uploadSession } from "../api/backend";

const ALLOWED_EXTENSIONS = ["mp4", "mp3", "wav", "m4a"];

export default function Upload() {
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);

  function isAllowedFile(candidateFile) {
    if (!candidateFile?.name) {
      return false;
    }

    const ext = candidateFile.name.split(".").pop()?.toLowerCase();
    return ALLOWED_EXTENSIONS.includes(ext);
  }

  function handlePickedFile(candidateFile) {
    if (!candidateFile) {
      return;
    }

    if (!isAllowedFile(candidateFile)) {
      setError("Unsupported file type. Use mp4, mp3, wav, or m4a.");
      return;
    }

    setError("");
    setFile(candidateFile);
  }

  async function handleSubmit(event) {
    // Prevent full page refresh so React can handle submit state.
    event.preventDefault();
    setMessage("");
    setError("");

    // Basic client-side checks before we call the backend.
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
      // Send upload request through our shared API helper.
      const payload = await uploadSession({ title: title.trim(), file });
      setMessage(payload.message || "Upload successful.");
      setTitle("");
      setFile(null);
    } catch (err) {
      setError(err.message || "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>Upload Session</h1>

      <form className="upload-form" onSubmit={handleSubmit}>
        <div>
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
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={(event) => {
            event.preventDefault();
            setIsDragOver(false);
            handlePickedFile(event.dataTransfer.files?.[0]);
          }}
        >
          <label htmlFor="file">Recording</label>
          <input
            id="file"
            type="file"
            accept=".mp4,.mp3,.wav,.m4a"
            onChange={(event) => handlePickedFile(event.target.files?.[0])}
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

      {message ? <p className="success-text">{message}</p> : null}
      {error ? <p className="error-text">{error}</p> : null}
    </div>
  );
}
