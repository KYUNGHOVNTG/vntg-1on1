import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoadingOverlay } from './core/loading';
import { LandingPage } from './pages/LandingPage';
import { Dashboard } from './domains/dashboard/pages';

function App() {
  return (
    <>
      {/* 전역 로딩 오버레이 */}
      <LoadingOverlay />

      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;