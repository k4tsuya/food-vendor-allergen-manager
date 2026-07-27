import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../authContext.jsx';
import { apiFetch } from '../api.js';

function AdminAccountPage() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match.');
      return;
    }

    if (!window.confirm('Change your password? You will need to log in again.')) {
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
      setError(err.message);
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

      <form className="admin-form" onSubmit={handleSubmit}>
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

        {error && <p className="login-error">{error}</p>}

        <div className="admin-form-actions">
          <button type="submit" className="login-submit">Change password</button>
        </div>
      </form>
    </div>
  );
}

export default AdminAccountPage;