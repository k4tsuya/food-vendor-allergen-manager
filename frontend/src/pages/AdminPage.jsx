import { useEffect, useState } from 'react';
import { useAuth } from '../authContext.jsx';
import { apiFetch } from '../api.js';
import Modal from '../components/Modal';

function AdminPage() {
  const { token, logout } = useAuth();
  const [allergens, setAllergens] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [code, setCode] = useState('');
  const [descriptionEn, setDescriptionEn] = useState('');
  const [descriptionNl, setDescriptionNl] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadAllergens = () => {
    setIsLoading(true);
    apiFetch('/allergens', token)
      .then((data) => {
        setAllergens(data);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    loadAllergens();
  }, []);

  const resetForm = () => {
    setCode('');
    setDescriptionEn('');
    setDescriptionNl('');
    setEditingId(null);
  };

  const handleAddNew = () => {
    resetForm();
    setIsModalOpen(true);
  };

  const handleEdit = (allergen) => {
    setEditingId(allergen.id);
    setCode(allergen.code);
    setDescriptionEn(allergen.description_en);
    setDescriptionNl(allergen.description_nl);
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (editingId) {
        await apiFetch(`/allergens/${editingId}`, token, {
          method: 'PUT',
          body: JSON.stringify({ description_en: descriptionEn, description_nl: descriptionNl }),
        });
      } else {
        await apiFetch('/allergens', token, {
          method: 'POST',
          body: JSON.stringify({ code, description_en: descriptionEn, description_nl: descriptionNl }),
        });
      }
      resetForm();
      setIsModalOpen(false);
      loadAllergens();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this allergen?')) return;

    try {
      await apiFetch(`/allergens/${id}`, token, { method: 'DELETE' });
      loadAllergens();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="app">
      <div className="admin-header">
        <h1>Admin Area</h1>
        <button onClick={logout} className="language-switcher">Log out</button>
      </div>

    <div className="admin-section-header">
    <h2 className="admin-section-title">Allergens</h2>
    <button onClick={handleAddNew} className="login-submit admin-add-button">
        Add allergen
    </button>
    </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? 'Edit allergen' : 'Add allergen'}
      >
        <form className="admin-form" onSubmit={handleSubmit}>
          <label className="login-field">
            Code
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              disabled={!!editingId}
              required
            />
          </label>
          <label className="login-field">
            English description
            <input
              type="text"
              value={descriptionEn}
              onChange={(e) => setDescriptionEn(e.target.value)}
              required
            />
          </label>
          <label className="login-field">
            Dutch description
            <input
              type="text"
              value={descriptionNl}
              onChange={(e) => setDescriptionNl(e.target.value)}
              required
            />
          </label>

          {error && <p className="login-error">{error}</p>}

          <div className="admin-form-actions">
            <button type="submit" className="login-submit">
              {editingId ? 'Save changes' : 'Add allergen'}
            </button>
          </div>
        </form>
      </Modal>

      {isLoading ? (
        <p className="loading-message">Loading...</p>
      ) : (
        <table className="admin-table">
          <thead>
            <tr>
              <th>Code</th>
              <th>English</th>
              <th>Dutch</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {allergens.map((allergen) => (
              <tr key={allergen.id}>
                <td>{allergen.code}</td>
                <td>{allergen.description_en}</td>
                <td>{allergen.description_nl}</td>
                <td className="admin-row-actions">
                  <button onClick={() => handleEdit(allergen)} className="admin-link-button">
                    Edit
                  </button>
                  <button onClick={() => handleDelete(allergen.id)} className="admin-link-button admin-delete">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default AdminPage;