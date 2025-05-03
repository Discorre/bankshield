// jest.config.js
module.exports = {
    testEnvironment: 'jsdom',
    // файлы, которые Jest будет считать тестами
    testMatch: ['**/?(*.)+(spec|test).[jt]s?(x)'],
  
    // ищем модули в node_modules и в src
    moduleDirectories: ['node_modules', 'src'],
    moduleFileExtensions: ['js', 'jsx', 'json', 'node'],
  
    // подключаем setupTests.js
    setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  
    // все .js/.jsx/.ts/.tsx файлы пропускаем через babel-jest
    transform: {
      '^.+\\.[jt]sx?$': 'babel-jest',
    },
  
    // НЕ игнорируем axios — он тоже идёт через Babel
    transformIgnorePatterns: [
      '/node_modules/(?!(axios)/)'
    ],
  
    // чтобы наверняка: маппим axios на CommonJS-сборку
    moduleNameMapper: {
      '^axios$': require.resolve('axios/dist/node/axios.cjs'),
      '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    },
  };
  