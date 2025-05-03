import React, { useContext, useState, useEffect } from 'react';
import { CartContext } from '../App';
import api from '../api/api';

const Cart = () => {
  const { user } = useContext(CartContext);
  const [basketItems, setBasketItems] = useState([]);
  const API_URL = process.env.REACT_APP_API_URL;

  const fetchBasket = async () => {
    try {
      const response = await api.get(`${API_URL}/basket`);
          
      setBasketItems(response.data);
    } catch (error) {
      if (error.a)
      console.error('Ошибка получения корзины:', error);
    }
  };

  useEffect(() => {
    fetchBasket();
  }, [user]);

  const removeItem = (basket_item_id) => {
    api.delete(`${API_URL}/basket/${basket_item_id}`, {})
    .then(response => {
      fetchBasket();
    })
    .catch(error => {
      alert(error.response?.data?.detail || 'Ошибка при удалении элемента');
    });
  };
  

  if (!user) {
    return (
      <div className="cart-container">
        <h2>Корзина</h2>
        <p>Для просмотра корзины, пожалуйста, войдите в аккаунт.</p>
      </div>
    );
  }

  return (
    <div className="cart-container">
      <h2>Корзина</h2>
      {basketItems.length === 0 ? (
        <p>Корзина пуста</p>
      ) : (
        <ul>
          {basketItems.map((item) => (
            <li key={item.basket_item_id}>
              <span key={item.basket_id}>{item.name} - {item.price} руб/месяц</span>
              <button onClick={() => removeItem(item.basket_id)}>Удалить</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Cart;
