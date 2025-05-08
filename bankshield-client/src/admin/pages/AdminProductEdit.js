import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const AdminProductEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const API_URL = process.env.REACT_APP_API_URL;
  const token = localStorage.getItem('adminAccessToken');

  const [product, setProduct] = useState({
    name: '',
    description: '',
    full_description: '',
    price: ''
  });

  useEffect(() => {
    axios.get(`${API_URL}/allproducts/${id}`)
      .then(res => setProduct(res.data))
      .catch(() => alert('Ошибка при загрузке данных продукта'));
  }, [id]);

  const handleChange = (e) => {
    setProduct({ ...product, [e.target.name]: e.target.value });
  };

  const handleSave = (e) => {
    e.preventDefault();
  
    axios.patch(`${API_URL}/products?prod_id=${product.id}`, product, {
      headers: { Authorization: token }
    })
    .then(() => {
      alert('Продукт обновлён');
      navigate('/admin/products');
    })
    .catch(() => alert('Ошибка при сохранении'));
  };

  return (
    <div className="form-container">
      <h2>Редактировать продукт</h2>
      <form onSubmit={handleSave}>
        <input
          type="text"
          name="name"
          placeholder="Название"
          value={product.name}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="description"
          placeholder="Краткое описание"
          value={product.description}
          onChange={handleChange}
          required
        />
        <textarea
          name="full_description"
          placeholder="Полное описание"
          value={product.full_description}
          onChange={handleChange}
          required
          rows={8}
          cols={50}
        />
        <input
          type="number"
          name="price"
          placeholder="Цена"
          value={product.price}
          onChange={handleChange}
          required
        />
        <button type="submit">Сохранить изменения</button>
      </form>
    </div>
  );
};

export default AdminProductEdit;
