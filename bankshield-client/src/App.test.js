// src/App.test.js

import React from 'react';
import { render, screen, act } from '@testing-library/react';
import App from './App';
import Header from './components/Header';
import { MemoryRouter } from 'react-router-dom';
import api from './api/api';

jest.mock('./api/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(() => Promise.resolve({ data: [] })),
    post: jest.fn(() => Promise.resolve({ data: {} })),
  },
}));

jest.mock('axios', () => ({
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  patch: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: jest.fn(() => ({})), // по умолчанию возвращает пустой объект
  useNavigate: jest.fn(() => jest.fn()),
}));

// Перед всеми тестами включаем fake-таймеры
beforeAll(() => {
  jest.useFakeTimers();
});
afterAll(() => {
  jest.useRealTimers();
});

beforeEach(() => {
  jest.spyOn(window, 'alert').mockImplementation(() => {});
});

afterEach(() => {
  jest.clearAllMocks();
});


describe('App — базовые проверки', () => {
  test('Рендерится без ошибок и сначала показывает спиннер', () => {
    render(<App />);
    // Спиннер должен появиться сразу
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  test('Проверяет, что Header существует', () => {
    expect(Header).toBeDefined();
  });

  test('App компонент не вызывает ошибок при рендеринге', () => {
    expect(() => render(<App />)).not.toThrow();
  });
});
