import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Register = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');

  const API_URL = process.env.REACT_APP_API_URL;

  const passwordRegex = /(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}/;

  const handlePasswordChange = (e) => {
    const newPassword = e.target.value;
    setPassword(newPassword);

    if (!passwordRegex.test(newPassword)) {
      setPasswordError('Пароль должен содержать минимум 6 символов, включая цифру, заглавную и строчную буквы, а также спецсимвол (!@#$%^&*).');
    } else {
      setPasswordError('');
    }

    // Проверяем совпадение с confirm password
    if (confirmPassword && newPassword !== confirmPassword) {
      setConfirmPasswordError('Пароли не совпадают');
    } else {
      setConfirmPasswordError('');
    }
  };

  const handleConfirmPasswordChange = (e) => {
    const value = e.target.value;
    setConfirmPassword(value);

    if (value !== password) {
      setConfirmPasswordError('Пароли не совпадают');
    } else {
      setConfirmPasswordError('');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setConfirmPasswordError('Пароли не совпадают');
      return;
    }

    axios.post(`${API_URL}/register`, { username, email, password })
      .then(response => {
        alert(response.data.message);
        navigate('/login');
      })
      .catch(error => {
        alert(error.response?.data?.detail || 'Ошибка регистрации');
      });
  };

  return (
    <div className="form-container">
      <h2>Регистрация</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Имя"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={handlePasswordChange}
          required
        />
        {passwordError && <p className="error-message">{passwordError}</p>}

        <input
          type="password"
          placeholder="Подтвердите пароль"
          value={confirmPassword}
          onChange={handleConfirmPasswordChange}
          required
        />
        {confirmPasswordError && <p className="error-message">{confirmPasswordError}</p>}

        <button type="submit" disabled={!!passwordError || !!confirmPasswordError}>
          Зарегистрироваться
        </button>
      </form>
    </div>
  );
};

export default Register;