// Use an env override when needed; otherwise rely on Vite proxy (/api -> backend).
const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

function getToken() {
  return localStorage.getItem("token");
}

async function request(path, options = {}) {
  // Central request helper so all endpoints share one error-handling pattern.
  const headers = { ...options.headers };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // If the server says 401, the token is bad or expired — clear it and let
  // the caller handle the redirect (ProtectedRoute will kick to /login).
  if (response.status === 401) {
    localStorage.removeItem("token");
    window.dispatchEvent(new CustomEvent("auth:expired"));
    throw new Error("Session expired. Please log in again.");
  }

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

// --- Auth ---

export function loginUser(email, password) {
  return request("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export function registerUser(name, email, password) {
  return request("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
}

export function getMe() {
  return request("/api/auth/me");
}

// --- Courses ---

export function createCourse(name) {
  return request("/api/courses/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export function joinCourse(inviteCode) {
  return request("/api/courses/join", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ invite_code: inviteCode }),
  });
}

export function getCourses() {
  return request("/api/courses/");
}

export function getCourse(courseId) {
  return request(`/api/courses/${courseId}`);
}

export function getCourseSessions(courseId) {
  return request(`/api/courses/${courseId}/sessions`);
}

export function updateMemberRole(courseId, userId, role) {
  return request(`/api/courses/${courseId}/members/${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role }),
  });
}

// --- Sessions ---

export function getSessions() {
  return request("/api/sessions/");
}

export function searchSessions(query) {
  const params = new URLSearchParams({ q: query });
  return request(`/api/sessions/search?${params.toString()}`);
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

// --- Transcripts ---

export function getTranscript(sessionId) {
  return request(`/api/transcripts/${sessionId}`);
}

// --- Notes ---

export function getNotes(sessionId) {
  return request(`/api/notes/session/${sessionId}`);
}
