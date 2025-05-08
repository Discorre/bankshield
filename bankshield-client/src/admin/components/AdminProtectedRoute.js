import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { CartContext } from '../../App';

const AdminProtectedRoute = ({ children }) => {
  useContext(CartContext);

  const access_token = localStorage.getItem('adminAccessToken');
  if (access_token == null) {
    return <Navigate to="/admin/login" replace />;
  }
  return children;
};

export default AdminProtectedRoute;
