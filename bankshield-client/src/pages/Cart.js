// src/pages/Cart.js
import React, { useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { CartContext } from '../App';

const Cart = () => {
  const { user } = useContext(CartContext);
  const [basketItems, setBasketItems] = useState([]);

  const fetchBasket = () => {
    if (user) {
      axios.get(`http://localhost:8000/basket/${user.id}`)
        .then(response => setBasketItems(response.data))
        .catch(error => console.error('Ошибка получения корзины:', error));
    }
  };

  useEffect(() => {
    fetchBasket();
  }, [user]);

  const removeItem = (basket_item_id) => {
    axios.delete(`http://localhost:8000/basket/${user.id}/${basket_item_id}`)
      .then(response => {
        fetchBasket();
      })
      .catch(error => {
        alert(error.response.data.detail || 'Ошибка при удалении элемента');
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
              <span>{item.name} - {item.price} руб/месяц</span>
              <button onClick={() => removeItem(item.id)}>Удалить</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Cart;
