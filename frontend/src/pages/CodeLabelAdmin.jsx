import { useEffect, useState } from 'react';
import { useAuth } from '../authContext.jsx';
import { apiFetch } from '../api.js';
import Modal from '../components/Modal.jsx';
import { Link } from 'react-router-dom';


function CodeLabelAdmin({ title, singularLabel, apiPath }) {
  const { token } = useAuth();
  const [entries, setEntries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const [code, setCode] = useState('');
  const [descriptionEn, setDescriptionEn] = useState('');
  const [descriptionNl, setDescriptionNl] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const loadEntries = () => {
    setIsLoading(true);
    apiFetch(apiPath, token)
      .then((data) => {
        setEntries(data);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    loadEntries();
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

  const handleEdit = (entry) => {
    setEditingId(entry.id);
    setCode(entry.code);
    setDescriptionEn(entry.description_en);
    setDescriptionNl(entry.description_nl);
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (editingId) {
        await apiFetch(`${apiPath}/${editingId}`, token, {
          method: 'PUT',
          body: JSON.stringify({ description_en: descriptionEn, description_nl: descriptionNl }),
        });
      } else {
        await apiFetch(apiPath, token, {
          method: 'POST',
          body: JSON.stringify({ code, description_en: descriptionEn, description_nl: descriptionNl }),
        });
      }
      resetForm();
      setIsModalOpen(false);
      loadEntries();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Delete this ${singularLabel}?`)) return;

    try {
      await apiFetch(`${apiPath}/${id}`, token, { method: 'DELETE' });
      loadEntries();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="admin-resource-section">
      <div className="admin-section-header">
        <div className="admin-section-header-left">
          <Link to="/admin" className="admin-back-link">← Back</Link>
          <h2 className="admin-section-title">{title}</h2>
        </div>
        <button onClick={handleAddNew} className="login-submit admin-add-button">
          Add {singularLabel}
        </button>
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? `Edit ${singularLabel}` : `Add ${singularLabel}`}
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
              {editingId ? 'Save changes' : `Add ${singularLabel}`}
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
            {entries.map((entry) => (
              <tr key={entry.id}>
                <td>{entry.code}</td>
                <td>{entry.description_en}</td>
                <td>{entry.description_nl}</td>
                <td className="admin-row-actions">
                  <button onClick={() => handleEdit(entry)} className="admin-link-button">
                    Edit
                  </button>
                  <button onClick={() => handleDelete(entry.id)} className="admin-link-button admin-delete">
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

export default CodeLabelAdmin;