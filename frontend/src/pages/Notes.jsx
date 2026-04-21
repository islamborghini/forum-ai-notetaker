import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getSession, getNotes, getTranscript } from "../api/backend";
import {
  getSessionStatusLabel,
  SESSION_STATUS_LABELS,
} from "../utils/sessionStatus";

function formatTimestamp(value) {
  if (!value) return "Unknown";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function formatSegmentTime(seconds) {
  const total = Math.max(0, Math.floor(Number(seconds) || 0));
  const hh = String(Math.floor(total / 3600)).padStart(2, "0");
  const mm = String(Math.floor((total % 3600) / 60)).padStart(2, "0");
  const ss = String(total % 60).padStart(2, "0");
  return `${hh}:${mm}:${ss}`;
}

const TERMINAL_STATUSES = ["notes_generated", "failed"];
const POLL_INTERVAL_MS = 4000;

export default function Notes() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [session, setSession] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [notes, setNotes] = useState(null);

  useEffect(() => {
    let cancelled = false;
    let timeoutId = null;
    let firstLoad = true;

    async function loadData() {
      if (firstLoad) {
        setLoading(true);
        setError("");
      }

      const results = await Promise.allSettled([
        getSession(id),
        getTranscript(id),
        getNotes(id),
      ]);
      if (cancelled) return;

      if (results[0].status === "rejected") {
        if (firstLoad) {
          setError(results[0].reason?.message || "Failed to load session.");
          setLoading(false);
        } else {
          timeoutId = setTimeout(loadData, POLL_INTERVAL_MS);
        }
        return;
      }

      const sess = results[0].value.data;
      setSession(sess);
      if (results[1].status === "fulfilled" && results[1].value?.data) {
        setTranscript(results[1].value.data);
      }
      if (results[2].status === "fulfilled" && results[2].value?.data) {
        setNotes(results[2].value.data);
      }
      if (firstLoad) setLoading(false);
      firstLoad = false;

      if (!TERMINAL_STATUSES.includes(sess?.status)) {
        timeoutId = setTimeout(loadData, POLL_INTERVAL_MS);
      }
    }

    loadData();

    return () => {
      cancelled = true;
      if (timeoutId) clearTimeout(timeoutId);
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
  const KNOWN_STATUSES = Object.keys(SESSION_STATUS_LABELS);
  const topics = notes?.topics || [];
  const actionItems = notes?.action_items || [];
  const segments = Array.isArray(transcript?.segments) ? transcript.segments : [];
  const hasTranscript = Boolean(transcript?.content);
  const hasNotes = Boolean(notes);

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>{session?.title || `Session ${id}`}</h1>
          {session?.original_filename ? (
            <p className="muted-text">Original file: {session.original_filename}</p>
          ) : null}
        </div>
      </div>

      <div className="notes-meta">
        <div className="notes-meta-item">
          <span className="notes-meta-label">Status</span>
          <strong>{getSessionStatusLabel(status)}</strong>
        </div>
        <div className="notes-meta-item">
          <span className="notes-meta-label">Last updated</span>
          <strong>{formatTimestamp(session?.updated_at)}</strong>
        </div>
      </div>

      {status === "processing" ? (
        <p className="status-processing" role="status" aria-live="polite">
          We&apos;re still processing this recording.
        </p>
      ) : null}

      {status === "failed" ? (
        <p className="error-text" role="alert">
          Processing failed. The recording could not be transcribed.
        </p>
      ) : null}

      <section className="notes-section">
        <h2 className="section-heading">Study Notes</h2>

        {hasNotes ? (
          <div className="notes-stack">
            <div className="notes-block">
              <h3>Summary</h3>
              <p>{notes.summary}</p>
            </div>

            <div className="notes-block">
              <h3>Topics</h3>
              {topics.length > 0 ? (
                <ul className="notes-list">
                  {topics.map((topic, index) => (
                    <li key={`${topic}-${index}`}>{topic}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted-text">No topics were extracted yet.</p>
              )}
            </div>

            <div className="notes-block">
              <h3>Action Items</h3>
              {actionItems.length > 0 ? (
                <ul className="notes-list">
                  {actionItems.map((item, index) => (
                    <li key={`${item}-${index}`}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted-text">No action items were identified.</p>
              )}
            </div>
          </div>
        ) : status === "transcribed" ? (
          <p className="muted-text">
            The transcript is ready. Study notes will appear here once generation finishes.
          </p>
        ) : status === "uploaded" || status === "processing" ? (
          <p className="muted-text">
            Study notes will appear here after the recording is processed.
          </p>
        ) : null}
      </section>

      <section className="notes-section">
        <h2 className="section-heading">Transcript</h2>

        {hasTranscript ? (
          <div className="notes-block">
            {segments.length > 0 ? (
              <ol className="transcript-segments">
                {segments.map((seg, index) => (
                  <li key={`${seg.start}-${index}`}>
                    <span className="transcript-timestamp">
                      {formatSegmentTime(seg.start)}
                    </span>
                    <span className="transcript-text">{seg.text}</span>
                  </li>
                ))}
              </ol>
            ) : (
              <p>{transcript.content}</p>
            )}
          </div>
        ) : status === "uploaded" ? (
          <p className="muted-text">Waiting for processing to start...</p>
        ) : status === "processing" ? (
          <p className="muted-text">Transcript will appear here once processing is complete.</p>
        ) : null}
      </section>

      {!hasTranscript && !hasNotes && status && !KNOWN_STATUSES.includes(status) ? (
        <p className="muted-text">Content not yet available.</p>
      ) : null}
    </div>
  );
}
