import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { CartContext } from '../App';
import "../App.css";

const Home = () => {
  const [products, setProducts] = useState([]);
  const { user } = useContext(CartContext);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get('http://localhost:8000/products')
      .then(response => setProducts(response.data))
      .catch(error => console.error('Ошибка при получении продуктов:', error));
  }, []);

  const addToCart = (product) => {
    if (!user) {
      alert('Пожалуйста, войдите в аккаунт для добавления в корзину');
      navigate('/login');
      return;
    }
    
    // Преобразуем объект продукта в формат, ожидаемый бэкендом
    const basketItem = {
      product_id: product.id,
      name: product.name,
      description: product.description,
      full_description: product.full_description,
      price: product.price,
      image: product.image || ""
    };
  
    axios.post(`http://localhost:8000/basket/${user.id}`, basketItem)
      .then(response => {
        alert(`Добавлено в корзину: ${product.name}`);
      })
      .catch(error => {
        alert(error.response.data.detail || 'Ошибка добавления в корзину');
      });
  };

  const goToDetails = (id) => {
    navigate(`/service/${id}`);
  };

  return (
    <div>
      {/* Hero Section */}
      <section className="hero" id="hero">
        <div className="hero-content">
          <h1>Защита банковских данных</h1>
          <p>Передовые решения для кибербезопасности в банковской сфере</p>
        </div>
      </section>

      {/* Services Section */}
       <section className="services" id="services">
        <div className="container">
          <h2>Наши услуги</h2>
          <div className="service-grid">
            {products.map(product => (
              <div className="service-card" key={product.id}>
                <h3>{product.name}</h3>
                <p>{product.description.substring(0, 100)}</p>
                <p className="price">Цена: {product.price} руб/месяц</p>
                <div className="button-container">
                    <button className="detail-btn" onClick={() => goToDetails(product.id)}>
                        Подробнее
                    </button>
                    <button className="detail-btn" onClick={() => addToCart(product)}>
                        В корзину
                    </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="about" id="about">
        <div className="container">
          <div className="about-content">
            <div className="about-text">
              <h2>О компании</h2>
              <p>BankShield – лидер в области кибербезопасности для банковских учреждений. Мы предлагаем комплексные решения для защиты финансовых данных от современных киберугроз.</p>
              <p>Наши эксперты с многолетним опытом используют передовые технологии, чтобы обеспечить надёжную защиту систем и транзакций.</p>
              <p>Мы стремимся к постоянному совершенствованию и гарантируем высокий уровень безопасности для наших клиентов.</p>
            </div>
            <div className="about-image">
              <img src="../bank.png" alt="О компании" />
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="contact" id="contact">
        <div className="container">
          <h2>Контакты</h2>
          <form onSubmit={(e) => {
            e.preventDefault();
            alert('Ваш запрос отправлен. Мы свяжемся с вами в ближайшее время.');
            e.target.reset();
          }}>
            <input type="text" name="name" placeholder="Ваше имя" required />
            <input type="email" name="email" placeholder="Ваш Email" required />
            <textarea name="message" rows="5" placeholder="Ваше сообщение" required></textarea>
            <button type="submit">Отправить</button>
          </form>
        </div>
      </section>
      <footer>
      <div className="container">
        <p>&copy; 2024 BankShield. Все права защищены.</p>
      </div>
    </footer>
    </div>

    
  );
};

export default Home;



