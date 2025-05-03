// src/setupTests.js
import '@testing-library/jest-dom';

// Мокаем react-router
jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }) => <>{children}</>,
  Routes: ({ children }) => <>{children}</>,
  Route: ({ element }) => element,
}));

// Мокаем спиннер
jest.mock('react-spinners', () => ({
  ClipLoader: ({ loading }) =>
    loading ? <div data-testid="spinner">Loading…</div> : null,
}));

// Мокаем свой API-модуль
jest.mock('./api/api', () => ({
  post: jest.fn(() => Promise.resolve({})),
}));

// Лёгкий мок localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
global.localStorage = localStorageMock;
