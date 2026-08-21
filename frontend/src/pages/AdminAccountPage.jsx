import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../authContext.jsx';
import { apiFetch } from '../api.js';
import Modal from '../components/Modal.jsx';

function AdminAccountPage() {
  const { token, logout, isOwner } = useAuth();
  const navigate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [admins, setAdmins] = useState([]);
  const [isLoadingAdmins, setIsLoadingAdmins] = useState(isOwner);
  const [newUsername, setNewUsername] = useState('');
  const [newAccountPassword, setNewAccountPassword] = useState('');
  const [accountsError, setAccountsError] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const loadAdmins = () => {
    setIsLoadingAdmins(true);
    apiFetch('/admins', token)
      .then((data) => {
        setAdmins(data);
        setIsLoadingAdmins(false);
      })
      .catch((err) => {
        setAccountsError(err.message);
        setIsLoadingAdmins(false);
      });
  };

  useEffect(() => {
    if (isOwner) {
      loadAdmins();
    }
  }, [isOwner]);

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setPasswordError('');

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match.');
      return;
    }

    if (!window.confirm('Confirm to change your password. You will need to log in again.')) {
      return;
    }

    try {
      await apiFetch('/auth/password', token, {
        method: 'PUT',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });
      logout();
      navigate('/login');
    } catch (err) {
      setPasswordError(err.message);
    }
  };

  const openAddModal = () => {
    setNewUsername('');
    setNewAccountPassword('');
    setAccountsError('');
    setIsAddModalOpen(true);
  };

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    setAccountsError('');

    try {
      await apiFetch('/admins', token, {
        method: 'POST',
        body: JSON.stringify({ username: newUsername, password: newAccountPassword }),
      });
      setNewUsername('');
      setNewAccountPassword('');
      setIsAddModalOpen(false);
      loadAdmins();
    } catch (err) {
      setAccountsError(err.message);
    }
  };

  const handleDeleteAdmin = async (admin) => {
    if (!window.confirm(`Delete manager account '${admin.username}'?`)) return;

    try {
      await apiFetch(`/admins/${admin.id}`, token, { method: 'DELETE' });
      loadAdmins();
    } catch (err) {
      setAccountsError(err.message);
    }
  };

  return (
    <div className="admin-resource-section">
      <div className="admin-section-header">
        <div className="admin-section-header-left">
          <Link to="/admin" className="admin-back-link">← Back</Link>
          <h2 className="admin-section-title">Account</h2>
        </div>
      </div>

      <form className="admin-form" onSubmit={handlePasswordSubmit}>
        <label className="login-field">
          Current password
          <input
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            required
          />
        </label>

        <label className="login-field">
          New password
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />
        </label>

        <label className="login-field">
          Confirm new password
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </label>

        {passwordError && <p className="login-error">{passwordError}</p>}

        <div className="admin-form-actions">
          <button type="submit" className="login-submit">Change password</button>
        </div>
      </form>

      {isOwner && (
        <>
          <div className="admin-landing-divider">
            <span>Account manager</span>
          </div>

          <div className="admin-section-header">
            <div className="admin-section-header-left" />
            <button onClick={openAddModal} className="login-submit admin-add-button">
              Add manager
            </button>
          </div>

          <Modal
            isOpen={isAddModalOpen}
            onClose={() => setIsAddModalOpen(false)}
            title="Add manager"
          >
            <form className="admin-form" onSubmit={handleCreateAdmin}>
              <label className="login-field">
                Username
                <input
                  type="text"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  required
                />
              </label>

              <label className="login-field">
                Password
                <input
                  type="password"
                  value={newAccountPassword}
                  onChange={(e) => setNewAccountPassword(e.target.value)}
                  minLength={8}
                  required
                />
              </label>

              {accountsError && <p className="login-error">{accountsError}</p>}

              <div className="admin-form-actions">
                <button type="submit" className="login-submit">Add manager</button>
              </div>
            </form>
          </Modal>

          {!isAddModalOpen && accountsError && <p className="login-error">{accountsError}</p>}

          {isLoadingAdmins ? (
            <p className="loading-message">Loading...</p>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Role</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {admins.map((admin) => (
                  <tr key={admin.id}>
                    <td>{admin.username}</td>
                    <td>{admin.role}</td>
                    <td className="admin-row-actions">
                      {admin.role !== 'owner' ? (
                        <button
                          onClick={() => handleDeleteAdmin(admin)}
                          className="admin-link-button admin-delete"
                        >
                          Delete
                        </button>
                      ) : (
                        <span className="admin-link-button admin-delete-placeholder" aria-hidden="true">
                          Delete
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  );
}

export default AdminAccountPage;