import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { CartContext } from '../App';

const ProtectedRoute = ({ children }) => {
  useContext(CartContext);

  const access_token = localStorage.getItem('accessToken');
  if (access_token == null) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
