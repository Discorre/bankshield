# tests/test_routes.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import Product, User, Roles, UserRole, RefreshToken, BasketItem, Appeals
from conftest import db_session, client

# ==============================
# Тест регистрации
# ==============================

def test_add_product_as_admin_logout(client):
    # Регистрация админа
    register_admin_response = client.post("/api/v1/admin/register", json={
        "username": "admin",
        "email": "admin@example.com",
        "password": "password123!"
    })
    assert register_admin_response.status_code == 200

    # Вход админа
    login_response = client.post("/api/v1/admin/login", json={
        "email": "admin@example.com",
        "password": "password123!"
    })
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Добавление товара
    product_data = {
        "name": "Тестовый товар",
        "description": "Описание товара",
        "full_description": "Полное описание",
        "price": 99.99
    }

    response = client.post(
        "/api/v1/products",
        json=product_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    # Выход
    logout_response = client.post("/api/v1/logout", headers={"refresh-token": refresh_token})
    assert logout_response.status_code == 200

# ==============================
# Тест добавления продукта (админ)
# ==============================

def test_add_product_as_admin_logout(client):
    # Регистрация админа
    register_admin_response = client.post("/api/v1/admin/register", json={
        "username": "admin",
        "email": "admin@example.com",
        "password": "password123!"
    })
    assert register_admin_response.status_code == 200

    # Вход админа
    login_response = client.post("/api/v1/admin/login", json={
        "email": "admin@example.com",
        "password": "password123!"
    })
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Добавление товара
    product_data = {
        "name": "Тестовый товар",
        "description": "Описание товара",
        "full_description": "Полное описание",
        "price": 99.99
    }

    response = client.post(
        "/api/v1/products",
        json=product_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    # Выход
    logout_response = client.post("/api/v1/logout", headers={"refresh-token": refresh_token})
    assert logout_response.status_code == 200

# # ==============================
# # Тест добавления продукта (обычный пользователь — запрещено)
# # ==============================

def test_add_product_as_user_forbidden(client):
    # Регистрация пользователя
    register_response = client.post("/api/v1/register", json={
        "username": "userforbidden",
        "email": "forbidden@example.com",
        "password": "password123!"
    })
    assert register_response.status_code == 200

    # Вход пользователя
    login_response = client.post("/api/v1/login", json={
        "email": "forbidden@example.com",
        "password": "password123!"
    })
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Попытка добавить товар — должно быть запрещено
    product_data = {
        "name": "Запрещённый товар",
        "description": "Не должен добавиться",
        "full_description": "",
        "price": 10.99
    }

    response = client.post(
        "/api/v1/products",
        json=product_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403

    # Выход
    logout_response = client.post("/api/v1/logout", headers={"refresh-token": refresh_token})
    assert logout_response.status_code == 200
# # ==============================
# # Тест корзины
# # ==============================

def test_add_to_basket(client):
    # Регистрация пользователя
    register_response = client.post("/api/v1/register", json={
        "username": "basketuser",
        "email": "basket@example.com",
        "password": "password123!"
    })
    assert register_response.status_code == 200

    # Вход
    login_response = client.post("/api/v1/login", json={
        "email": "basket@example.com",
        "password": "password123!"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    # Получаем первый товар
    product_response = client.get("/api/v1/products")
    assert product_response.status_code == 200
    product_id = product_response.json()[0]["id"]

    # Добавляем товар в корзину
    response = client.post("/api/v1/basket", json={"product_id": product_id}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "id" in response.json()

    # Выход
    logout_response = client.post("/api/v1/logout", headers={"refresh-token": refresh_token})
    assert logout_response.status_code == 200

# # ==============================
# # Тест отправки обращения
# # ==============================

def test_send_appeal(client):
    # Регистрация пользователя
    register_response = client.post("/api/v1/register", json={
        "username": "appealuser",
        "email": "appeal@example.com",
        "password": "password123!"
    })
    assert register_response.status_code == 200

    # Вход
    login_response = client.post("/api/v1/login", json={
        "email": "appeal@example.com",
        "password": "password123!"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]

    appeal_data = {
        "username_appeal": "testuser",
        "email_appeal": "appeal@example.com",
        "text_appeal": "Проблема с оплатой"
    }
   
    response = client.post(
        "/api/v1/appeal",
        json=appeal_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "рассмотрено" in response.json()["message"]

    # Выход
    logout_response = client.post("/api/v1/logout", headers={"refresh-token": refresh_token})
    assert logout_response.status_code == 200