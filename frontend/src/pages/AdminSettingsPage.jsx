import { useEffect, useState, useRef } from 'react';
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
  const [importError, setImportError] = useState('');
  const [importSuccess, setImportSuccess] = useState(false);
  const fileInputRef = useRef(null);

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

const handleExport = async () => {
  const response = await fetch('http://localhost:8000/data/export', {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json();

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `backup-${new Date().toISOString().slice(0, 10)}.json`;
  link.click();
  URL.revokeObjectURL(url);
};

const handleImportFileSelected = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  setImportError('');
  setImportSuccess(false);

  if (!window.confirm('This will REPLACE all items, allergens, meat types, categories, and settings with the contents of this file. This cannot be undone. Continue?')) {
    e.target.value = '';
    return;
  }

  try {
    const text = await file.text();
    const data = JSON.parse(text);

    await apiFetch('/data/import', token, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    setImportSuccess(true);
  } catch (err) {
    setImportError(err.message || 'Import failed. Check the file is a valid export.');
  }

  e.target.value = '';
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
      <div className="admin-resource-section">
  <div className="admin-section-header">
    <h2 className="admin-section-title">Backup & Restore</h2>
  </div>

  <div className="admin-backup-actions">
    <button onClick={handleExport} className="login-submit">
      Export all data
    </button>

    <div>
      <button
        onClick={() => fileInputRef.current.click()}
        className="login-submit admin-import-button"
      >
        Import data
      </button>
      <input
        type="file"
        accept="application/json"
        ref={fileInputRef}
        onChange={handleImportFileSelected}
        style={{ display: 'none' }}
      />
    </div>
  </div>

  {importSuccess && <p className="admin-settings-saved">Data imported successfully. Refresh other admin pages to see the changes.</p>}
  {importError && <p className="login-error">{importError}</p>}
</div>
    </div>
  );
}

export default AdminSettingsPage;