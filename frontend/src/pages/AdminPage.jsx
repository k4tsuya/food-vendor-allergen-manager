import { useAuth } from '../authContext.jsx';

function AdminPage() {
  const { logout } = useAuth();

  return (
    <div className="app">
      <h1>Admin Area</h1>
      <p>Item, allergen, and meat type management will go here.</p>
      <button onClick={logout} className="language-switcher">Log out</button>
    </div>
  );
}

export default AdminPage;