// api.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const api = axios.create({
  baseURL: `${API_URL}`,
});

// Флаг, чтобы не запускать несколько обновлений одновременно
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Перехватчик ответа
api.interceptors.response.use(
  res => res,
  async error => {
    const originalRequest = error.config;

    // Если access_token истёк
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return axios(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      isRefreshing = true;

      try {
        const refreshToken = localStorage.getItem('adminRefreshToken');
        const response = await axios.post(`${API_URL}/refresh`, {}, {
          headers: {
            'Authorization': refreshToken,
          },
        });

        const newAccessToken = response.data.access_token;
        localStorage.setItem('adminAccessToken', newAccessToken);

        api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
        processQueue(null, newAccessToken);

        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (err) {
        processQueue(err, null);
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('adminAccessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

export default api;
