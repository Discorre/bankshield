import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { CartContext } from '../../App';
import axios from 'axios';

const AdminLogin = () => {
  const { saveAuthAdmin } = useContext(CartContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL;

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/admin/login`, {
        email,
        password
      });

      const { admin, access_token, refresh_token } = response.data;

      localStorage.setItem('adminAccessToken', access_token);
      localStorage.setItem('adminRefreshToken', refresh_token);
      localStorage.setItem('adminUser', JSON.stringify(admin));
      saveAuthAdmin(admin)

      navigate('/admin/products');
    } catch (error) {
      alert(error.response?.data?.detail || 'Ошибка входа администратора');
    }
  };

  return (
    <div className="form-container">
      <h2>Вход для администратора</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          required
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Пароль"
          required
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
        <button type="submit">Войти</button>
      </form>
    </div>
  );
};

export default AdminLogin;
