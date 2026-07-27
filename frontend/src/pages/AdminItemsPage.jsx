import { useEffect, useState } from 'react';
import { useAuth } from '../authContext.jsx';
import { apiFetch } from '../api.js';
import Modal from '../components/Modal';
import { Link } from 'react-router-dom';
import { useLanguage } from '../localization.jsx';

function AdminItemsPage() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [allergens, setAllergens] = useState([]);
  const [meatTypes, setMeatTypes] = useState([]);
  const [meatTrackingEnabled, setMeatTrackingEnabled] = useState(false);
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [name, setName] = useState('');
  const [categoryKey, setCategoryKey] = useState('');
  const [selectedAllergens, setSelectedAllergens] = useState([]);
  const [selectedMeatTypes, setSelectedMeatTypes] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [warnings, setWarnings] = useState([]);
  const [page, setPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);

  const { language } = useLanguage();
  const PAGE_SIZE = 25;

const loadAll = () => {
  setIsLoading(true);
  const offset = (page - 1) * PAGE_SIZE;

  Promise.all([
    apiFetch(`/items?limit=${PAGE_SIZE}&offset=${offset}`, token),
    apiFetch('/allergens', token),
    apiFetch('/config', token),
    apiFetch('/meat-types', token),
    apiFetch('/categories', token),
  ]).then(([itemsData, allergensData, configData, meatTypesData, categoriesData]) => {
    setItems(itemsData);
    setHasNextPage(itemsData.length === PAGE_SIZE);
    setAllergens(allergensData);
    setMeatTrackingEnabled(configData.meat_tracking_enabled);
    setMeatTypes(configData.meat_tracking_enabled ? meatTypesData : []);
    setCategories(categoriesData);
    setIsLoading(false);
  });
};


useEffect(() => {
  loadAll();
}, [page]);

  const resetForm = () => {
    setName('');
    setCategoryKey('');
    setSelectedAllergens([]);
    setSelectedMeatTypes([]);
    setEditingId(null);
    setWarnings([]);
  };

  const handleAddNew = () => {
    resetForm();
    setIsModalOpen(true);
  };

  const handleEdit = (item) => {
    setEditingId(item.id);
    setName(item.name);
    setCategoryKey(item.category_key || '');
    setSelectedAllergens(item.allergens.map((a) => a.code));
    setSelectedMeatTypes(item.meat_types.map((m) => m.code));
    setWarnings([]);
    setIsModalOpen(true);
  };

  const toggleAllergen = (code) => {
    setSelectedAllergens((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const toggleMeatType = (code) => {
    setSelectedMeatTypes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const payload = {
      name,
      category_key: categoryKey || null,
      allergen_codes: selectedAllergens,
      meat_type_codes: selectedMeatTypes,
    };

    try {
      const result = editingId
        ? await apiFetch(`/items/${editingId}`, token, {
            method: 'PUT',
            body: JSON.stringify(payload),
          })
        : await apiFetch('/items', token, {
            method: 'POST',
            body: JSON.stringify(payload),
          });

      if (result.warnings && result.warnings.length > 0) {
        setWarnings(result.warnings);
        return;
      }

      resetForm();
      setIsModalOpen(false);
      loadAll();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this item?')) return;

    try {
      await apiFetch(`/items/${id}`, token, { method: 'DELETE' });
      loadAll();
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
          <h2 className="admin-section-title">Items</h2>
        </div>
        <button onClick={handleAddNew} className="login-submit admin-add-button">
          Add item
        </button>
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? 'Edit item' : 'Add item'}
      >
        <form className="admin-form" onSubmit={handleSubmit}>
          <label className="login-field">
            Name
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </label>

          <label className="login-field">
            Category
            <select value={categoryKey} onChange={(e) => setCategoryKey(e.target.value)}>
              <option value="">No category</option>
              {categories.map((category) => (
                <option key={category.code} value={category.code}>
                  {category.description_en}
                </option>
              ))}
            </select>
          </label>

          <div className="filter-group">
            <span className="filter-group-label">Allergens</span>
            <div className="filter-chips">
              {allergens.map((allergen) => (
                <label key={allergen.id} className="filter-chip">
                  <input
                    type="checkbox"
                    checked={selectedAllergens.includes(allergen.code)}
                    onChange={() => toggleAllergen(allergen.code)}
                  />
                  {allergen.description_en}
                </label>
              ))}
            </div>
          </div>

          {meatTrackingEnabled && meatTypes.length > 0 && (
            <div className="filter-group">
              <span className="filter-group-label">Meat types</span>
              <div className="filter-chips">
                {meatTypes.map((meatType) => (
                  <label key={meatType.id} className="filter-chip">
                    <input
                      type="checkbox"
                      checked={selectedMeatTypes.includes(meatType.code)}
                      onChange={() => toggleMeatType(meatType.code)}
                    />
                    {meatType.description_en}
                  </label>
                ))}
              </div>
            </div>
          )}

          {warnings.length > 0 && (
            <div className="admin-warnings">
              {warnings.map((w) => (
                <p key={w} className="login-error">{w}</p>
              ))}
              <button type="button" onClick={handleSubmit} className="login-submit">
                Save anyway
              </button>
            </div>
          )}

          {error && <p className="login-error">{error}</p>}

          <div className="admin-form-actions">
            <button type="submit" className="login-submit">
              {editingId ? 'Save changes' : 'Add item'}
            </button>
          </div>
        </form>
      </Modal>

      <table className="admin-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Allergens</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>{item.name}</td>
              <td>{item.category_key ? (categories.find((c) => c.code === item.category_key)?.description_en || item.category_key) : '—'}</td>
              <td>{item.allergens.map((a) => a.description_en).join(', ') || '—'}</td>
              <td className="admin-row-actions">
                <button onClick={() => handleEdit(item)} className="admin-link-button">
                  Edit
                </button>
                <button onClick={() => handleDelete(item.id)} className="admin-link-button admin-delete">
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>

      </table>
        <div className="pagination">
          <button
            onClick={() => setPage((p) => p - 1)}
            disabled={page === 1}
            className="admin-link-button"
          >
            ← {language === 'nl' ? 'Vorige' : 'Previous'}
          </button>
          <span className="pagination-info">
            {language === 'nl' ? 'Pagina' : 'Page'} {page}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasNextPage}
            className="admin-link-button"
          >
            {language === 'nl' ? 'Volgende' : 'Next'} →
          </button>
        </div>
    </div>
  );
}

export default AdminItemsPage;