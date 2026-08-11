import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const API_BASE = 'http://localhost:8000';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('admin_token'));
  const [isValidating, setIsValidating] = useState(true);
  const [role, setRole] = useState(null);


  
  useEffect(() => {
    if (!token) {
      setIsValidating(false);
      return;
    }

    fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        if (!response.ok) {
          localStorage.removeItem('admin_token');
          setToken(null);
          return null;
        }
        return response.json();
      })
      .then((data) => {
        if (data) {
          setRole(data.role);
        }
      })
      .finally(() => setIsValidating(false));
  }, [token]);

  const login = async (username, password) => {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Invalid username or password');
    }

    const data = await response.json();
    localStorage.setItem('admin_token', data.access_token);
    setToken(data.access_token);

    const meResponse = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    const meData = await meResponse.json();
    setRole(meData.role);
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    setToken(null);
    setRole(null);
  };

  return (
    <AuthContext.Provider
      value={{ token, role, isOwner: role === 'owner', login, logout, isAuthenticated: !!token, isValidating }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
