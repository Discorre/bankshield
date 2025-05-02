import React, { useState, useContext } from 'react';
import { CartContext } from '../App';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';

const ChangePassword = () => {
  const { user } = useContext(CartContext);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const navigate = useNavigate();

  const passwordRegex = /(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}/;

  const handleNewPasswordChange = (e) => {
    const newPassword = e.target.value;
    setNewPassword(newPassword);
    
    if (!passwordRegex.test(newPassword)) {
      setPasswordError('Пароль должен содержать минимум 6 символов, включая цифру, заглавную и строчную буквы, а также спецсимвол (!@#$%^&*).');
    } else {
      setPasswordError('');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!user) {
      alert('Пожалуйста, войдите в аккаунт.');
      return;
    }
    if (passwordError) return;
    
    const accessToken = localStorage.getItem('accessToken');
    api.patch('http://localhost:8000/api/v1/change_password', {
        old_password: oldPassword,
        new_password: newPassword
      }, {
        headers: { Authorization: `Bearer ${accessToken}` }
      })
      .then(() => alert('Пароль успешно изменён'))
      .catch(error => {
        if (error.response.status === 401) {
          alert('Сессия истекла. Авторизуйтесь снова');
          navigate('/login');
        } else {
          alert('Ошибка: ' + error.response.data.detail);
        }
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
          onChange={handleNewPasswordChange} 
          required 
        />
        {passwordError && <p className="error-message">{passwordError}</p>}
        <button type="submit" disabled={!!passwordError}>Сменить пароль</button>
      </form>
    </div>
  );
};

export default ChangePassword;
