import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './Dashboard';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import { isAuthenticated } from './lib/auth';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={isAuthenticated() ? <Navigate to="/" replace /> : <LoginPage />} />
        <Route path="/signup" element={isAuthenticated() ? <Navigate to="/" replace /> : <SignupPage />} />
        <Route
          path="/"
          element={(
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          )}
        />
      </Routes>
    </Router>
  );
}
