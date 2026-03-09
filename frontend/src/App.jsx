import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { UploadPage } from './pages/UploadPage'
import { SessionsPage } from './pages/SessionsPage'
import { TranscriptPage } from './pages/TranscriptPage'

export default function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<Navigate to="/upload" replace />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/sessions" element={<SessionsPage />} />
          <Route path="/sessions/:id" element={<TranscriptPage />} />
          <Route path="*" element={<Navigate to="/upload" replace />} />
        </Routes>
      </ErrorBoundary>
    </BrowserRouter>
  )
}
