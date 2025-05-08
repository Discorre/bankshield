import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Header from './components/Header';
import AdminHeader from './admin/components/AdminHeader';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Cart from './pages/Cart';
import ServiceDetails from './pages/ServiceDetails';
import ChangePassword from './pages/ChangePassword';
import ProtectedRoute from './components/ProtectedRoute';
import PublicOnlyRoute from './components/PublicOnlyRoute';
import AdminLogin from './admin/pages/AdminLogin';
import AdminProductList from './admin/pages/AdminProductList';
import AdminProtectedRoute from './admin/components/AdminProtectedRoute';
import AdminProductEdit from './admin/pages/AdminProductEdit';

const InnerApp = () => {
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin');

  return (
    <>
      {isAdminRoute ? <AdminHeader /> : <Header />}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/service/:id" element={<ServiceDetails />} />
        <Route path="/login" element={<PublicOnlyRoute><Login /></PublicOnlyRoute>} />
        <Route path="/register" element={<PublicOnlyRoute><Register /></PublicOnlyRoute>} />
        <Route path="/cart" element={<ProtectedRoute><Cart /></ProtectedRoute>} />
        <Route path="/change_password" element={<ProtectedRoute><ChangePassword /></ProtectedRoute>} />
        <Route path="/admin/login" element={<PublicOnlyRoute><AdminLogin /></PublicOnlyRoute>} />
        <Route path="/admin/products" element={<AdminProtectedRoute><AdminProductList /></AdminProtectedRoute>} />
        <Route path="/admin/product/:id" element={<AdminProtectedRoute><AdminProductEdit/></AdminProtectedRoute>}/>
      </Routes>
    </>
  );
};

export default InnerApp;