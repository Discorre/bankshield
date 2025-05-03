import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Cart from './pages/Cart';
import ServiceDetails from './pages/ServiceDetails';
import ChangePassword from './pages/ChangePassword';
import ProtectedRoute from "./components/ProtectedRoute";
import PublicOnlyRoute from "./components/PublicOnlyRoute"
import { ClipLoader } from 'react-spinners';
import api from './api/api';

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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen w-screen fixed top-0 left-0">
        <ClipLoader size={500} color={"#123abc"} loading={loading} />
      </div>
    );
  }

  return (
    <div data-testid="app-root">
      <CartContext.Provider value={{ cartItems, setCartItems, user, token, saveAuth, logout }}>
        <Router>
          <Header />
          <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/service/:id" element={<ServiceDetails />} />

          <Route path="/login" element={<PublicOnlyRoute><Login /></PublicOnlyRoute>} />
          <Route path="/register" element={<PublicOnlyRoute><Register /></PublicOnlyRoute>} /> 

          <Route 
            path="/cart"
            element={<ProtectedRoute>
              <Cart />
            </ProtectedRoute>} />
          <Route 
            path="/change_password"
            element={<ProtectedRoute><ChangePassword /></ProtectedRoute>} />
        </Routes>
      </Router>
    </CartContext.Provider>
  </div>
  );
}

export default App;
