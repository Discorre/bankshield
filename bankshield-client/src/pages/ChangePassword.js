// src/pages/ChangePassword.js
import React, { useState, useContext } from 'react';
import axios from 'axios';
import { CartContext } from '../App';
import { useNavigate } from 'react-router-dom';

const ChangePassword = () => {
  const { user } = useContext(CartContext);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!user) {
      alert('Пожалуйста, войдите в аккаунт.');
      return;
    }
    axios.put('http://localhost:8000/change_password', {
      email: user.email,
      old_password: oldPassword,
      new_password: newPassword
    })
      .then(response => {
        alert(response.data.message);
        navigate('/');
      })
      .catch(error => {
        alert(error.response.data.detail || 'Ошибка смены пароля');
      });
  };

  return (
    <div className="form-container">
      <h2>Смена пароля</h2>
      <form onSubmit={handleSubmit}>
        <input 
          type="password" 
          placeholder="Старый пароль" 
          value={oldPassword} 
          onChange={e => setOldPassword(e.target.value)} 
          required 
        />
        <input 
          type="password" 
          placeholder="Новый пароль" 
          value={newPassword} 
          onChange={e => setNewPassword(e.target.value)} 
          required 
        />
        <button type="submit">Сменить пароль</button>
      </form>
    </div>
  );
};

export default ChangePassword;
