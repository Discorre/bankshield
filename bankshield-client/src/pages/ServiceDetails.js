import React, { useState, useEffect } from 'react';
import api from '../api/api';
import { useParams, useNavigate } from 'react-router-dom';

const ServiceDetails = () => {
  const { id } = useParams();
  const [service, setService] = useState(null);
  const navigate = useNavigate();

  const API_URL = process.env.REACT_APP_API_URL;

  useEffect(() => {
    api.get(`${API_URL}/products/${id}`)
      .then(response => setService(response.data))
      .catch(error => {
        alert('Услуга не найдена');
        navigate('/');
      });
  }, [id, navigate, API_URL]);
  

  if (!service) return <p>Загрузка...</p>;

  return (
    <div className="container" style={{ padding: '40px 0' }}>
      <div className="service-details">
        <h2>{service.name}</h2>
        <p>{service.full_description || service.description}</p>
        <p style={{ fontSize: '18px', fontWeight: 'bold', marginTop: '20px' }}>
          Цена: {service.price} руб/месяц
        </p>
        <button className="detail-btn" style={{ marginTop: '20px' }} onClick={() => navigate(-1)}>
          Вернуться назад
        </button>
      </div>
    </div>
  );
};

export default ServiceDetails;
