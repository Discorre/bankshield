import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Register = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');

  const passwordRegex = /(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}/;

  const handlePasswordChange = (e) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    
    if (!passwordRegex.test(newPassword)) {
      setPasswordError('Пароль должен содержать минимум 6 символов, включая цифру, заглавную и строчную буквы, а также спецсимвол (!@#$%^&*).');
    } else {
      setPasswordError('');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:8000/api/v1/register', { username, email, password })
      .then(response => {
        alert(response.data.message);
        navigate('/login');
      })
      .catch(error => {
        alert(error.response.data.detail || 'Ошибка регистрации');
      });
  };

  return (
    <div className="form-container">
      <h2>Регистрация</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Имя" value={username} onChange={e => setUsername(e.target.value)} required />
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input type="password" placeholder="Пароль" value={password} onChange={handlePasswordChange} required />
        {passwordError && <p className="error-message">{passwordError}</p>}
        <button type="submit" disabled={!!passwordError}>Зарегистрироваться</button>
      </form>
    </div>
  );
};

export default Register;