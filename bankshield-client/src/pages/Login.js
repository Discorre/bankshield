// src/pages/Login.js
import React, { useState, useContext } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { CartContext } from '../App';

const Login = () => {
  const { saveAuth } = useContext(CartContext);
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:8000/login', { email, password })
      .then(response => {
        alert(response.data.message);
        saveAuth(response.data.user, response.data.access_token);
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
