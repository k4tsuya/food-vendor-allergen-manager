const API_BASE = 'http://localhost:8000';

export async function apiFetch(path, token, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (response.status === 401) {
    localStorage.removeItem('admin_token');
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

if (!response.ok) {
  const errorBody = await response.json().catch(() => ({}));

  let message = `Request failed with status ${response.status}`;
  if (typeof errorBody.detail === 'string') {
    message = errorBody.detail;
  } else if (Array.isArray(errorBody.detail) && errorBody.detail.length > 0) {
    message = errorBody.detail
      .map((e) => e.msg.replace(/^Value error, /, ''))
      .join(' ');
  }

  throw new Error(message);
}
  if (response.status === 204) {
    return null;
  }

  return response.json();
}