# Forum AI Notetaker — Frontend

React SPA for the CS162 Final Project. Students upload class recordings and the app transcribes them automatically, making notes available to the whole course.

## Stack

| Tool | Version | Purpose |
|------|---------|---------|
| React | 19 | UI framework |
| Vite | 7 | Dev server + bundler |
| React Router | 7 | Client-side routing |
| CSS Modules | — | Component-scoped styles |
| Vitest | 4 | Test runner |
| React Testing Library | 16 | Component + hook testing |

## Getting Started

```bash
cp .env.example .env        # add your VITE_API_URL
npm install
npm run dev                 # http://localhost:5173
```

**Environment variables:**

| Variable | Example | Required |
|----------|---------|----------|
| `VITE_API_URL` | `http://localhost:5000` | Yes |

## Commands

```bash
npm run dev       # start dev server with HMR
npm run build     # production build → dist/
npm run preview   # preview production build locally
npm run lint      # ESLint
npx vitest run    # run all 51 tests
```

## Project Structure

```
src/
├── styles/
│   └── design-system.css        # All design tokens (fonts, colors, spacing)
├── pages/
│   ├── UploadPage.jsx            # Split-screen upload UI
│   ├── SessionsPage.jsx          # Session list
│   └── TranscriptPage.jsx        # Transcript viewer + live polling
├── hooks/
│   ├── useUpload.js              # Upload state machine (useReducer)
│   ├── useSessions.js            # Fetch session list
│   └── useTranscript.js          # Fetch + poll transcript
├── components/
│   ├── layout/                   # PageLayout, Navbar, Panel, GridBackground
│   ├── common/                   # Button, StatusBadge, ErrorBoundary, EmptyState
│   ├── upload/                   # DropZone, DropZoneDisplay
│   ├── sessions/                 # SessionCard, SessionsSkeleton
│   ├── transcript/               # TranscriptCard, TranscriptSkeleton
│   └── icons/                    # DocumentIcon, FileIcon
├── api/
│   └── client.js                 # XHR upload (with progress + abort), fetch wrapper
├── utils/
│   └── index.js                  # cn, normalizeStatus, formatFileSize, formatDate, ...
├── constants/
│   └── index.js                  # MAX_FILE_SIZE_BYTES, ACCEPTED_MIME_TYPES, ...
└── fixtures/
    ├── sessions.js               # MOCK_SESSIONS (dev only)
    └── transcripts.js            # MOCK_TRANSCRIPTS, MOCK_SEGMENTS (dev only)
```

## Routes

| Path | Page | Notes |
|------|------|-------|
| `/` | → `/upload` | redirect |
| `/upload` | `UploadPage` | |
| `/sessions` | `SessionsPage` | |
| `/sessions/:id` | `TranscriptPage` | |
| `*` | → `/upload` | 404 fallback |

## Key Patterns

### Upload state machine

`useUpload` manages the full upload lifecycle via `useReducer`:

```
idle → file-selected → preparing → uploading → success
                   ↘                        ↗
                    error ←────────────────
                      ↓
                   retry → file-selected
```

Public API:

```js
const {
  phase, file, progress, sessionId, error,  // state
  selectFile, removeFile, cancel, retry,    // actions
  startUpload,                              // (onProgress) => Promise
} = useUpload()
```

`startUpload` takes a function `(onProgress) => Promise` — the page is responsible for providing the upload function, the hook manages all state transitions.

### XHR upload with progress

```js
import { api } from './api/client.js'

upload.startUpload((onProgress) => api.uploadRecording(file, onProgress))
```

`uploadRecording` returns a Promise with an `.abort()` method attached for cancellation support.

### Design system

All colors, typography, and spacing are CSS custom properties defined in `design-system.css` and imported once in `main.jsx`. CSS modules reference them via `var(--token-name)`. Hardcoding hex values anywhere else is a bug.

Key tokens:

```css
--bg-base: #0A0909           /* page background */
--bg-surface: #1B1919        /* panel/card background */
--text-primary: #E5E0DD      /* main text */
--text-secondary: #968F8C    /* meta text */
--accent: #E11D48            /* red (focus rings, semantic) */
--accent-link: #1DBFBA       /* teal (browse link only) */
--progress-fill: #4A7FA5     /* steel blue upload bar */
--font-sans: 'DM Sans'
--font-mono: 'JetBrains Mono'
```

### Polling

`TranscriptPage` polls every 5 seconds while a session is processing. The refetch does not trigger a loading spinner — only the initial load does.

```js
useEffect(() => {
  if (!isProcessing) return
  const interval = setInterval(refetch, POLL_INTERVAL_MS)
  return () => clearInterval(interval)
}, [isProcessing, refetch])
```

## Testing

51 tests across 7 files. Run with `npx vitest run`.

| File | Tests |
|------|-------|
| `utils/index.test.js` | 24 |
| `hooks/useUpload.test.js` | 7 |
| `hooks/useTranscript.test.js` | 5 |
| `hooks/useSessions.test.js` | 3 |
| `api/client.test.js` | 4 |
| `components/common/Button.test.jsx` | 5 |
| `components/common/StatusBadge.test.jsx` | 3 |

## MVP Status

The frontend currently runs on mock data from `src/fixtures/`. To connect a real backend, swap `useSessions` and `useTranscript` to call `api.getSessions()` and `api.getTranscript(id)` respectively. The upload flow via `api.uploadRecording` is already wired and ready.
