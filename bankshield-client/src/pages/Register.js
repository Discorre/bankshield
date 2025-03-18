// src/pages/Register.js
import React, { useState/*, useContext*/ } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
//import { CartContext } from '../App';

const Register = () => {
  //const { saveAuth } = useContext(CartContext);
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('http://localhost:8000/register', { username, email, password })
      .then(response => {
        alert(response.data.message);
        //saveAuth(response.data.user, response.data.access_token);
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
        <input type="password" placeholder="Пароль" value={password} onChange={e => setPassword(e.target.value)} required />
        <button type="submit">Зарегистрироваться</button>
      </form>
    </div>
  );
};

export default Register;
