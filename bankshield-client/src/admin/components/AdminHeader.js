import React, {useContext} from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CartContext } from '../../App';

const AdminHeader = () => {
  const { user, admin_logout } = useContext(CartContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    admin_logout()
    navigate('/');
    
  };

  return (
    <header>
      <div className="container">
        <nav>
          <div className="logo">
            <Link to="/admin" style={{ color: '#fff', textDecoration: 'none' }}>
              AdminShield
            </Link>
          </div>
          <ul>
            <li><Link to="/admin/products">Продукты</Link></li>
            <li><Link to="/admin/orders">Заказы</Link></li>
            {user?.username && (
                
            <li className="username"> {user.username}</li>
            
            )}
            <li>
              <button
                onClick={handleLogout}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                Выйти
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default AdminHeader;
