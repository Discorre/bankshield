import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';

const AdminProductList = () => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [filterText, setFilterText] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const productsPerPage = 6; // количество продуктов на странице

  const [newProduct, setNewProduct] = useState({
    name: '',
    description: '',
    full_description: '',
    price: ''
  });

  const navigate = useNavigate();
  const API_URL = process.env.REACT_APP_API_URL;
  const token = localStorage.getItem('adminAccessToken');

  const fetchProducts = () => {
    api.get(`${API_URL}/products`)
      .then(res => {
        setProducts(res.data);
        setFilteredProducts(res.data); // изначально все товары
      })
      .catch(() => alert('Ошибка при загрузке продуктов'));
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // Фильтрация при изменении текста
  useEffect(() => {
    const filtered = products.filter(product =>
      product.name.toLowerCase().includes(filterText.toLowerCase())
    );
    setFilteredProducts(filtered);
    setCurrentPage(1); // сброс на первую страницу при новом поиске
  }, [filterText, products]);

  // Пагинация
  const indexOfLastProduct = currentPage * productsPerPage;
  const indexOfFirstProduct = indexOfLastProduct - productsPerPage;
  const currentProducts = filteredProducts.slice(indexOfFirstProduct, indexOfLastProduct);

  const totalPages = Math.ceil(filteredProducts.length / productsPerPage);

  const handleAddProduct = (e) => {
    e.preventDefault();
    api.post(`${API_URL}/products`, newProduct, {
      headers: { Authorization: token }
    })
      .then(() => {
        alert('Продукт успешно добавлен');
        setNewProduct({ name: '', description: '', full_description: '', price: '' });
        fetchProducts(); // обновляем список
      })
      .catch(err => {
        alert(err.response?.data?.detail || 'Доступ запрещен');
      });
  };

  const handleDelete = (id) => {
    if (!window.confirm('Удалить продукт?')) return;
    api.delete(`${API_URL}/products`, {
      params: { prod_id: id }
    })
      .then(() => {
        alert('Удалено');
        fetchProducts(); // обновляем список
      })
      .catch(() => alert('Доступ запрещен'));
  };

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className="container">
      <h2 className="services-title" style={{ textAlign: 'center', margin: '40px 0', color: '#0056b3' }}>
        Управление продуктами
      </h2>

      {/* Форма добавления */}
      <div className="form-container">
        <h2>Добавить продукт</h2>
        <form onSubmit={handleAddProduct}>
          <input
            type="text"
            placeholder="Название"
            value={newProduct.name}
            onChange={e => setNewProduct({ ...newProduct, name: e.target.value })}
            required
          />
          <input
            type="text"
            placeholder="Описание"
            value={newProduct.description}
            onChange={e => setNewProduct({ ...newProduct, description: e.target.value })}
            required
          />
          <textarea
            placeholder="Полное описание"
            value={newProduct.full_description}
            onChange={e => setNewProduct({ ...newProduct, full_description: e.target.value })}
            required
          />
          <input
            type="number"
            placeholder="Цена"
            value={newProduct.price}
            onChange={e => setNewProduct({ ...newProduct, price: e.target.value })}
            required
          />
          <button type="submit">Добавить</button>
        </form>
      </div>

      {/* Поиск и список товаров */}
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Фильтр по названию..."
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          style={{ width: '100%', padding: '10px', fontSize: '16px' }}
        />
      </div>

      <div className="services" style={{ padding: '40px 0' }}>
        <div className="service-grid">
          {currentProducts.length > 0 ? (
            currentProducts.map(product => (
              <div className="service-card" key={product.id}>
                <h3>{product.name}</h3>
                <p>{product.description}</p>
                <p className="price">{product.price} ₽</p>
                <div className="button-container">
                  <button
                    className="detail-btn"
                    onClick={() => navigate(`/admin/product/${product.id}`)}
                  >
                    Редактировать
                  </button>
                  <button
                    style={{
                      background: '#ff4d4f',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '4px',
                      padding: '8px 16px',
                      cursor: 'pointer',
                      transition: 'background 0.3s'
                    }}
                    onClick={() => handleDelete(product.id)}
                  >
                    Удалить
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p>Продукты не найдены.</p>
          )}
        </div>

        {/* Пагинация */}
        <div className="pagination" style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
          {Array.from({ length: totalPages }, (_, i) => (
            <button
              key={i + 1}
              onClick={() => paginate(i + 1)}
              disabled={currentPage === i + 1}
              style={{
                margin: '0 5px',
                padding: '8px 12px',
                fontWeight: currentPage === i + 1 ? 'bold' : 'normal',
                backgroundColor: currentPage === i + 1 ? '#007bff' : '#ddd',
                color: currentPage === i + 1 ? 'white' : 'black',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              {i + 1}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminProductList;