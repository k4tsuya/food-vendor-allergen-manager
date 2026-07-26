import { Routes, Route } from 'react-router-dom';
import './App.css';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import AllergensPage from './pages/AllergensPage';
import LoginPage from './pages/LoginPage';
import AdminPage from './pages/AdminPage';
import RequireAuth from './components/RequireAuth';

function App() {
  return (
    <div className="page">
      <Navbar />

      <Routes>
        <Route path="/" element={<AllergensPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/admin"
          element={
            <RequireAuth>
              <AdminPage />
            </RequireAuth>
          }
        />
      </Routes>

      <Footer />
    </div>
  );
}

export default App;