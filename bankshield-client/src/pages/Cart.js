import React, { useContext } from 'react';
import { CartContext } from '../App';

const Cart = () => {
  const { cartItems, setCartItems } = useContext(CartContext);

  const removeItem = (index) => {
    setCartItems(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="cart-container">
      <h2>Корзина</h2>
      {cartItems.length === 0 ? (
        <p>Корзина пуста</p>
      ) : (
        <ul>
          {cartItems.map((item, index) => (
            <li key={index}>
              <span>{item.name} - ${item.price}/месяц</span>
              <button onClick={() => removeItem(index)}>Удалить</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Cart;
