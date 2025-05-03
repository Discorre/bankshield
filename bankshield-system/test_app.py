import os
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy import text
from main import engine

# Load environment variables from .env
load_dotenv()

# Ensure required secrets are set in .env:
# TEST_DATABASE_URL, REDIS_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# import the app and Base
from main import app, Base, get_db

# Use TEST_DATABASE_URL for PostgreSQL
TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')
if not TEST_DATABASE_URL:
    pytest.exit("Please set the TEST_DATABASE_URL environment variable in .env for PostgreSQL tests", returncode=1)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use test DB
@pytest.fixture(scope="session")
def db_engine():
    # create tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # drop tables after session
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    # begin nested transaction for test isolation
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    # override get_db
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    monkeypatch.setattr('main.get_db', override_get_db)
    client = TestClient(app)
    return client

# Helper to load default products
@pytest.fixture(autouse=True)
def populate_products(db_session):
    # Load products.json next to main.py
    file_path = os.path.join(os.path.dirname(__file__), '..', 'products.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        from main import Product
        for p in products:
            db_session.add(Product(**p))
        db_session.commit()

# @pytest.fixture(scope="session", autouse=True)
# def wait_for_db():
#     import time
#     import psycopg2
#     for _ in range(10):
#         try:
#             conn = psycopg2.connect("postgresql://postgres:password@localhost:5432/postgres")
#             conn.close()
#             return
#         except psycopg2.OperationalError:
#             time.sleep(2)
#     raise Exception("PostgreSQL not ready")

# @pytest.fixture(autouse=True)
# def clean_tables(wait_for_db):
#     with engine.connect() as conn:
#         conn.execute(text("TRUNCATE users RESTART IDENTITY CASCADE"))
#         conn.commit()

# Tests for product endpoints

def test_get_all_products(client):
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.parametrize("invalid_id", ["nonexistent", "1234"])
def test_get_product_not_found(client, invalid_id):
    response = client.get(f"/api/v1/products/{invalid_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Продукт не найден"

# Tests for auth: register and login

def test_register_and_login(client):
    register_data = {"username": "testuser", "email": "test@example.com", "password": "secret"}
    r = client.post("/api/v1/register", json=register_data)
    assert r.status_code == 200
    assert r.json()["message"] == "Регистрация прошла успешно"

    # duplicate registration fails
    r2 = client.post("/api/v1/register", json=register_data)
    assert r2.status_code == 400

    # login
    login_data = {"email": "test@example.com", "password": "secret"}
    r3 = client.post("/api/v1/login", json=login_data)
    assert r3.status_code == 200
    payload = r3.json()
    assert "access_token" in payload
    assert "refresh_token" in payload
    assert payload["message"] == "Вход выполнен успешно"

# Tests for basket: add and delete

def test_basket_flow(client):
    client.post("/api/v1/register", json={"username": "buser", "email": "b@example.com", "password": "pwd"})
    login = client.post("/api/v1/login", json={"email": "b@example.com", "password": "pwd"}).json()
    token = login["access_token"]

    prod_list = client.get("/api/v1/products").json()
    if not prod_list:
        pytest.skip("No products available to test basket")
    product_id = prod_list[0]["id"]

    r_add = client.post(
        "/api/v1/basket",
        json={"product_id": product_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r_add.status_code == 200
    added = r_add.json()
    assert "id" in added
    assert added["product_id"] == product_id

    r_get = client.get(
        "/api/v1/basket",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r_get.status_code == 200
    basket = r_get.json()
    assert isinstance(basket, list)
    assert any(item["name"] == prod_list[0]["name"] for item in basket)

    basket_item_id = added["id"]
    r_del = client.delete(
        f"/api/v1/basket/{basket_item_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r_del.status_code == 200
    assert r_del.json()["message"] == "Элемент корзины удалён"
