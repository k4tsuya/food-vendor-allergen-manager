import { useEffect, useState } from 'react';
import { useAuth } from '../authContext.jsx';
import { apiFetch } from '../api.js';
import { Link } from 'react-router-dom';

function AdminSettingsPage() {
  const { token } = useAuth();
  const [meatTrackingEnabled, setMeatTrackingEnabled] = useState(false);
  const [companyName, setCompanyName] = useState('');
  const [navbarBrandEn, setNavbarBrandEn] = useState('');
  const [navbarBrandNl, setNavbarBrandNl] = useState('');
  const [defaultLanguage, setDefaultLanguage] = useState('nl');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    apiFetch('/config', token).then((data) => {
      setMeatTrackingEnabled(data.meat_tracking_enabled);
      setCompanyName(data.company_name);
      setNavbarBrandEn(data.navbar_brand_en);
      setNavbarBrandNl(data.navbar_brand_nl);
      setDefaultLanguage(data.default_language);
      setIsLoading(false);
    });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!window.confirm('Save these settings? This affects the entire site.')) {
      return;
    }

    setError('');
    setSaved(false);

    try {
      await apiFetch('/config', token, {
        method: 'PUT',
        body: JSON.stringify({
          meat_tracking_enabled: meatTrackingEnabled,
          company_name: companyName,
          navbar_brand_en: navbarBrandEn,
          navbar_brand_nl: navbarBrandNl,
          default_language: defaultLanguage,
        }),
      });
      setSaved(true);
    } catch (err) {
      setError(err.message);
    }
  };

  if (isLoading) {
    return <p className="loading-message">Loading...</p>;
  }

  return (
    <div className="admin-resource-section">
      <div className="admin-section-header">
        <div className="admin-section-header-left">
          <Link to="/admin" className="admin-back-link">← Back</Link>
          <h2 className="admin-section-title">Settings</h2>
        </div>
      </div>

      <form className="admin-form" onSubmit={handleSubmit}>
        <label className="login-field">
          Company name
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            required
          />
        </label>

        <label className="login-field">
          Navbar brand (English)
          <input
            type="text"
            value={navbarBrandEn}
            onChange={(e) => setNavbarBrandEn(e.target.value)}
            required
          />
        </label>

        <label className="login-field">
          Navbar brand (Dutch)
          <input
            type="text"
            value={navbarBrandNl}
            onChange={(e) => setNavbarBrandNl(e.target.value)}
            required
          />
        </label>

        <label className="login-field">
          Default language
          <select value={defaultLanguage} onChange={(e) => setDefaultLanguage(e.target.value)}>
            <option value="nl">Dutch</option>
            <option value="en">English</option>
          </select>
        </label>

        <label className="filter-chip">
          <input
            type="checkbox"
            checked={meatTrackingEnabled}
            onChange={(e) => setMeatTrackingEnabled(e.target.checked)}
          />
          Enable meat type tracking
        </label>

        {saved && <p className="admin-settings-saved">Settings saved.</p>}
        {error && <p className="login-error">{error}</p>}

        <div className="admin-form-actions">
          <button type="submit" className="login-submit">Save settings</button>
        </div>
      </form>
    </div>
  );
}

export default AdminSettingsPage;