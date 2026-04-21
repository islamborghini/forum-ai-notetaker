export const SESSION_STATUS_LABELS = {
  uploaded: "Uploaded",
  processing: "Processing",
  transcribed: "Transcript Ready",
  notes_generated: "Notes Ready",
  notes_failed: "Notes Failed",
  failed: "Failed",
};

export const SESSION_STATUS_FILTERS = [
  { value: "uploaded", label: "Uploaded" },
  { value: "processing", label: "Processing" },
  { value: "transcribed", label: "Transcript Ready" },
  { value: "notes_generated", label: "Notes Ready" },
  { value: "notes_failed", label: "Notes Failed" },
  { value: "failed", label: "Failed" },
];

export function getSessionStatusLabel(status) {
  return SESSION_STATUS_LABELS[status] || status || "Unknown";
}
