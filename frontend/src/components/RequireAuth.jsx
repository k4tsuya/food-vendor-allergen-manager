import { Navigate } from 'react-router-dom';
import { useAuth } from '../authContext.jsx';

function RequireAuth({ children }) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default RequireAuth;