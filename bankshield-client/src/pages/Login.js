import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { CartContext } from '../App';
import axios from 'axios';

const Login = () => {
  const { saveAuth } = useContext(CartContext);
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const API_URL = process.env.REACT_APP_API_URL;

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post(`${API_URL}/login`, { email, password })
      .then(response => {
        const { user, access_token, refresh_token } = response.data;
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('refreshToken', refresh_token);
        localStorage.setItem('user', JSON.stringify(user));
        saveAuth(user);
        navigate('/');
      })
      .catch(error => {
        alert(error.response.data.detail || 'Ошибка входа');
      });
  };

  return (
    <div className="form-container">
      <h2>Логин</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input type="password" placeholder="Пароль" value={password} onChange={e => setPassword(e.target.value)} required />
        <button type="submit">Войти</button>
      </form>
    </div>
  );
};

export default Login;
