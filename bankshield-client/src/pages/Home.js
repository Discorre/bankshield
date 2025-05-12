import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { CartContext } from '../App';
import "../App.css";
import api from '../api/api';

const Home = () => {
  const [products, setProducts] = useState([]);
  const { user } = useContext(CartContext);
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL;

  useEffect(() => {
    api.get(`${API_URL}/products`)
    .then(response => setProducts(response.data))
    .catch(error => {
      alert('Услуга не найдена');
    });
  }, [API_URL]);

  const addToCart = (product) => {
    if (!user) {
      alert('Пожалуйста, войдите в аккаунт для добавления в корзину');
      navigate('/login');
      return;
    }
    
    const basketItem = {product_id: product.id};
    api.post(`${API_URL}/basket`, basketItem)
    .then(() => {
      alert(`Добавлено в корзину: ${product.name}`);
    })
    .catch(error => {
      if (error.response.status === 401) {
        
        navigate('/login');
      } else if (error.response.status === 400) {
        alert('Товар уже в корзине');
      } else {
        console.log('Ошибка при добавлении в корзину:', error);
        console.log(basketItem);
        alert('Ошибка добавления');
      }
      })
  };

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post(
        `${API_URL}/appeal`,
        {
          username_appeal: formData.name,
          email_appeal: formData.email,
          text_appeal: formData.message
        }
      );
      alert('Ваш запрос отправлен. Мы свяжемся с вами в ближайшее время.');
      setFormData({ name: '', email: '', message: '' });
      console.log('Ответ сервера:', response.data);
    } catch (error) {
      alert('Ошибка при отправке формы.');
      console.error('Ошибка:', error.response?.data || error.message);
    }
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
      <script>alert("test");</script>
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
          <form onSubmit={handleSubmit}>
          <input
            type="text"
            name="name"
            placeholder="Ваше имя"
            required
            value={formData.name}
            onChange={handleChange}
          />
          <input
            type="email"
            name="email"
            placeholder="Ваш Email"
            required
            value={formData.email}
            onChange={handleChange}
          />
          <textarea
            name="message"
            rows="5"
            placeholder="Ваше сообщение"
            required
            value={formData.message}
            onChange={handleChange}
          ></textarea>
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



