// export default App;
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { ClipLoader } from 'react-spinners';
import api from './api/api';

import InnerApp from './InnerApp'; // Вынесем часть с useLocation в отдельный компонент

export const CartContext = React.createContext();

function App() {
  const [cartItems, setCartItems] = useState([]);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const API_URL = process.env.REACT_APP_API_URL;

  useEffect(() => {

    setTimeout(() => {
      const savedUser = localStorage.getItem('user');
      const savedToken = localStorage.getItem('token');
      if (savedUser && savedToken) {
        setUser(JSON.parse(savedUser));
        setToken(savedToken);
      }
      setLoading(false);
    }, 1000);
  }, []);

  const saveAuth = (userData, jwt) => {
    setUser(userData);
    setToken(jwt);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('token', jwt);
  };

  const saveAuthAdmin = (userData, jwt) => {
    setUser(userData);
    setToken(jwt);
    localStorage.setItem('admin', JSON.stringify(userData));
    localStorage.setItem('adminToken', jwt);
  };

  const logout = async () => {
    try {
      await api.post(`${API_URL}/logout`, {}, {
        headers: {
          'refresh-token': localStorage.getItem('refreshToken')
        }
      });

      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');

      window.location.href = '/';
    } catch (error) {
      console.error('Ошибка при выходе:', error.response?.data || error.message);
    }
  };

  const admin_logout = async () => {
    try {
      await api.post(`${API_URL}/logout`, {}, {
        headers: {
          'refresh-token': localStorage.getItem('adminRefreshToken')
        }
      });

      localStorage.removeItem('adminAccessToken');
      localStorage.removeItem('adminUser');

      window.location.href = '/';
    } catch (error) {
      console.error('Ошибка при выходе:', error.response?.data || error.message);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen w-screen fixed top-0 left-0">
        <ClipLoader size={500} color={"#123abc"} loading={loading} />
      </div>
    );
  }

  return (
    <CartContext.Provider value={{ cartItems, setCartItems, user, token, saveAuth, saveAuthAdmin, logout, admin_logout }}>
      <Router>
        <InnerApp />
      </Router>
    </CartContext.Provider>
  );
}

export default App;