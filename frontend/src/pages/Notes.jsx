import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getSession, getNotes, getTranscript } from "../api/backend";

export default function Notes() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [session, setSession] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [notes, setNotes] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setLoading(true);
      setError("");

      try {
        const results = await Promise.allSettled([
          getSession(id),
          getTranscript(id),
          getNotes(id),
        ]);

        if (cancelled) return;

        if (results[0].status === "rejected") {
          setError(results[0].reason?.message || "Failed to load session.");
          return;
        }

        setSession(results[0].value.data);

        if (results[1].status === "fulfilled") {
          setTranscript(results[1].value.data);
        }
        if (results[2].status === "fulfilled") {
          setNotes(results[2].value.data);
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Failed to load notes.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadData();

    return () => {
      cancelled = true;
    };
  }, [id]);

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

  const status = session?.status;

  const STATUS_LABELS = {
    uploaded: "Uploaded",
    processing: "Processing",
    transcribed: "Transcribed",
    notes_generated: "Ready",
    failed: "Failed",
  };
  const KNOWN_STATUSES = Object.keys(STATUS_LABELS);

  return (
    <div className="container">
      <h1>{session?.title || `Session ${id}`}</h1>
      {status ? (
        <p className="muted-text">Status: {STATUS_LABELS[status] || status}</p>
      ) : null}

      {status === "processing" ? (
        <p className="status-processing" role="status" aria-live="polite">
          Transcription in progress...
        </p>
      ) : null}

      {status === "failed" ? (
        <p className="error-text" role="alert">
          Processing failed. The recording could not be transcribed.
        </p>
      ) : null}

      {transcript ? (
        <>
          <h2>Transcript</h2>
          <p>{transcript.content}</p>
        </>
      ) : status === "uploaded" ? (
        <p className="muted-text">Waiting for processing to start...</p>
      ) : null}

      {notes ? (
        <>
          <h2>Notes</h2>
          <p>
            <strong>Summary:</strong> {notes.summary}
          </p>
          <p>
            <strong>Topics:</strong> {(notes.topics || []).join(", ")}
          </p>
          <p>
            <strong>Action items:</strong>{" "}
            {(notes.action_items || []).join(", ")}
          </p>
        </>
      ) : status === "transcribed" ? (
        <p className="muted-text">
          Transcript is ready. Notes will be generated soon.
        </p>
      ) : null}

      {!transcript && !notes && status &&
       !KNOWN_STATUSES.includes(status) ? (
        <p className="muted-text">Content not yet available.</p>
      ) : null}
    </div>
  );
}
