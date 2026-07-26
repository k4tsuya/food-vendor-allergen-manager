import { Link } from 'react-router-dom';

function AdminLandingPage() {
  return (
    <div className="admin-landing-grid">
      <Link to="/admin/allergens" className="admin-landing-card">
        <span className="admin-landing-card-title">Allergens</span>
        <span className="admin-landing-card-desc">Manage the allergen reference list</span>
      </Link>
      <Link to="/admin/meat-types" className="admin-landing-card">
        <span className="admin-landing-card-title">Meat Types</span>
        <span className="admin-landing-card-desc">Manage the meat type reference list</span>
      </Link>
    </div>
  );
}

export default AdminLandingPage;