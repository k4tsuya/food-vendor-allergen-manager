import { Link } from 'react-router-dom';

function AdminLandingPage() {
  return (
    <div>
      <div className="admin-landing-grid">
        <Link to="/admin/items" className="admin-landing-card">
          <span className="admin-landing-card-title">Items</span>
          <span className="admin-landing-card-desc">Manage items, their allergens, and categories</span>
        </Link>
      </div>

      <div className="admin-landing-divider">
        <span>Settings</span>
      </div>

      <div className="admin-landing-grid">
        <Link to="/admin/settings" className="admin-landing-card">
          <span className="admin-landing-card-title">Settings</span>
          <span className="admin-landing-card-desc">Company name, branding, default language, and feature toggles</span>
        </Link>
          <div className="admin-landing-grid">
        <Link to="/admin/account" className="admin-landing-card">
          <span className="admin-landing-card-title">Account</span>
          <span className="admin-landing-card-desc">Change your password</span>
        </Link>
      </div>
      </div>
      <div className="admin-landing-divider">
        <span>Reference data</span>
      </div>

      <div className="admin-landing-grid">
        <Link to="/admin/categories" className="admin-landing-card">
          <span className="admin-landing-card-title">Categories</span>
          <span className="admin-landing-card-desc">Manage item categories</span>
        </Link>
        <Link to="/admin/allergens" className="admin-landing-card">
          <span className="admin-landing-card-title">Allergens</span>
          <span className="admin-landing-card-desc">Manage the allergen reference list</span>
        </Link>
        <Link to="/admin/meat-types" className="admin-landing-card">
          <span className="admin-landing-card-title">Meat Types</span>
          <span className="admin-landing-card-desc">Manage the meat type reference list</span>
        </Link>
      </div>
    </div>
  );
}

export default AdminLandingPage;