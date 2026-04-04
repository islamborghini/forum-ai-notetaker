// Use an env override when needed; otherwise rely on Vite proxy (/api -> backend).
const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  // Central request helper so all endpoints share one error-handling pattern.
  const response = await fetch(`${API_BASE}${path}`, options);
  const rawText = await response.text();
  let payload = null;

  if (rawText) {
    try {
      payload = JSON.parse(rawText);
    } catch {
      payload = { message: rawText };
    }
  }

  // Backend returns { success, message, data }, so check both HTTP and API-level failures.
  if (!response.ok || payload?.success === false) {
    throw new Error(payload?.error || payload?.message || "Request failed");
  }

  return payload;
}

export function getSessions() {
  return request("/api/sessions");
}

export function uploadSession({ title, file }) {
  // File uploads must be sent as multipart/form-data.
  const formData = new FormData();
  formData.append("title", title);
  formData.append("file", file);

  return request("/api/sessions/upload", {
    method: "POST",
    body: formData,
  });
}

export function getTranscript(sessionId) {
  return request(`/api/transcripts/${sessionId}`);
}

export function getNotes(sessionId) {
  return request(`/api/notes/session/${sessionId}`);
}
