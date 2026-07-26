import { Outlet } from 'react-router-dom';
import { useAuth } from '../authContext.jsx';

function AdminLayout() {
  const { logout } = useAuth();

  return (
    <div className="app">
      <div className="admin-header">
        <h1>Admin Area</h1>
        <button onClick={logout} className="language-switcher">Log out</button>
      </div>

      <Outlet />
    </div>
  );
}

export default AdminLayout;