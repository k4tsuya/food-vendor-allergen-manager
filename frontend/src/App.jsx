import { Routes, Route } from 'react-router-dom';
import './styles/base.css';
import './styles/navbar.css';
import './styles/matrix.css';
import './styles/filterbar.css';
import './styles/auth.css';
import './styles/admin.css';
import './styles/modal.css';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import AllergensPage from './pages/AllergensPage';
import LoginPage from './pages/LoginPage';
import AdminLayout from './components/AdminLayout';
import AdminLandingPage from './pages/AdminLandingPage';
import AdminAllergensPage from './pages/AdminAllergensPage';
import AdminMeatTypesPage from './pages/AdminMeatTypesPage';
import RequireAuth from './components/RequireAuth';
import AdminItemsPage from './pages/AdminItemsPage';
import AdminCategoriesPage from './pages/AdminCategoriesPage';

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
              <AdminLayout />
            </RequireAuth>
          }
        >
          <Route index element={<AdminLandingPage />} />
          <Route path="items" element={<AdminItemsPage />} />
          <Route path="allergens" element={<AdminAllergensPage />} />
          <Route path="meat-types" element={<AdminMeatTypesPage />} />
          <Route path="categories" element={<AdminCategoriesPage />} />
        </Route>
      </Routes>

      <Footer />
    </div>
  );
}

export default App;