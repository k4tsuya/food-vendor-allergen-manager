import { Navigate } from 'react-router-dom';
import { useAuth } from '../authContext.jsx';

function RequireAuth({ children }) {
  const { isAuthenticated, isValidating } = useAuth();

  if (isValidating) {
    return <p className="loading-message">Loading...</p>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default RequireAuth;