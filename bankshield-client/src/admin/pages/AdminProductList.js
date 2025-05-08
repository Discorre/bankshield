import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';

const AdminProductList = () => {
  const [products, setProducts] = useState([]);
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
      .then(res => setProducts(res.data))
      .catch(() => alert('Ошибка при загрузке продуктов'));
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleAddProduct = (e) => {
    console.log(token)
    e.preventDefault();
    api.post(`${API_URL}/products`, newProduct, {
      headers: { Authorization: token }
    })
    .then(() => {
      alert('Продукт успешно добавлен');
      setNewProduct({ name: '', description: '', full_description: '', price: '' });
      fetchProducts();
    })
    .catch(err => {
      alert(err.response?.data?.detail || 'Ошибка при добавлении');
    });
  };

  const handleDelete = (id) => {
    if (!window.confirm('Удалить продукт?')) return;
    api.delete(`${API_URL}/products`, {
      params: { prod_id: id }
    })
    .then(() => {
      alert('Удалено');
      fetchProducts();
    })
    .catch(() => alert('Ошибка при удалении'));
  };

  return (
    <div className="container">
      <h2 className="services-title" style={{ textAlign: 'center', margin: '40px 0', color: '#0056b3' }}>
        Управление продуктами
      </h2>

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

      <div className="services" style={{ padding: '40px 0' }}>
        <div className="service-grid">
          {products.map(product => (
            <div className="service-card" key={product.id}>
              <h3>{product.name}</h3>
              <p>{product.description}</p>
              <p className="price">{product.price} ₽</p>
              <div className="button-container">
                <button className="detail-btn" onClick={() => navigate(`/admin/product/${product.id}`)}>
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
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminProductList;
