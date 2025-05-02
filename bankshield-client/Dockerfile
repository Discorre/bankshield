# 1. Используем node для сборки
FROM node:18 AS builder

# 2. Устанавливаем рабочую директорию
WORKDIR /app

# 3. Копируем package.json и package-lock.json и устанавливаем зависимости
COPY package.json package-lock.json ./
RUN npm install

# 4. Копируем весь проект и собираем production-версию
COPY . .
RUN npm run build

# 5. Используем Nginx для раздачи собранного фронтенда
FROM nginx:alpine

# 6. Копируем файлы из билдера в папку Nginx
COPY --from=builder /app/build /usr/share/nginx/html

# 7. Копируем кастомный конфиг Nginx (если нужно)
#COPY nginx.conf /etc/nginx/conf.d/default.conf

# 8. Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
