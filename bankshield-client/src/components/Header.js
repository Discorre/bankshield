import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CartContext } from '../App';


const Header = () => {
  const { user, logout } = useContext(CartContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header data-testid="header">
      <div className="container">
        <nav>
          <div className="logo">
            <Link to="/" style={{ color: '#fff', textDecoration: 'none' }}>
              BankShield
            </Link>
          </div>
          <ul>
            <li><Link to="/admin/login">Вы админ?</Link></li>
            <li><Link to="/">Главная</Link></li>
            <li><a href="/#services">Услуги</a></li>
            <li><a href="/#about">О компании</a></li>
            <li><a href="/#contact">Контакты</a></li>
            {user ? (
              <>
                <li><Link to="/cart">Корзина</Link></li>
                <li><Link to="/change_password">Сменить пароль</Link></li>
                <li className="username"> {user.username}</li>
                <li>
                  <button 
                    onClick={handleLogout} 
                    style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                    Выход
                  </button>
                </li>
              </>
            ) : (
              <>
                <li><Link to="/login">Логин</Link></li>
                <li><Link to="/register">Регистрация</Link></li>
              </>
            )}
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
