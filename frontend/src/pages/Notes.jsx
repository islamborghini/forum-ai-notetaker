import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getNotes, getTranscript } from "../api/backend";

export default function Notes() {
  // This comes from route /notes/:id.
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [transcript, setTranscript] = useState(null);
  const [notes, setNotes] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError("");

      try {
        // Fetch transcript + notes together for faster page load.
        const [transcriptPayload, notesPayload] = await Promise.all([
          getTranscript(id),
          getNotes(id),
        ]);

        setTranscript(transcriptPayload.data);
        setNotes(notesPayload.data);
      } catch (err) {
        setError(err.message || "Failed to load notes.");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [id]);

  return (
    <div className="container">
      <h1>Session {id}</h1>

      {loading ? <p>Loading...</p> : null}
      {error ? <p>{error}</p> : null}

      {!loading && !error ? (
        <>
          <h2>Transcript</h2>
          <p>{transcript?.content || "Transcript not ready yet."}</p>

          <h2>Notes</h2>
          {notes ? (
            <>
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
          ) : (
            <p>Notes not generated yet.</p>
          )}
        </>
      ) : null}
    </div>
  );
}
