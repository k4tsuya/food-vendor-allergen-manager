import { useAuth } from '../authContext.jsx';
import CodeLabelAdmin from '../components/CodeLabelAdmin';

function AdminPage() {
  const { token, logout } = useAuth();

  return (
    <div className="app">
      <div className="admin-header">
        <h1>Admin Area</h1>
        <button onClick={logout} className="language-switcher">Log out</button>
      </div>

      <CodeLabelAdmin title="Allergens" singularLabel="allergen" apiPath="/allergens" token={token} />
      <CodeLabelAdmin title="Meat Types" singularLabel="meat type" apiPath="/meat-types" token={token} />
    </div>
  );
}

export default AdminPage;