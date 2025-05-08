# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Импортируем app и модели из main.py
from main import app, get_db, Base, populate_products, populate_roles

# Тестовая БД (должна совпадать с .env)
TEST_DATABASE_URL = "postgresql+psycopg2://discorre1:0412@db_test:5432/bankshield_test"

# Создаем движок и сессию
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределяем зависимость get_db
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

# Фикстура для работы с тестовой БД
@pytest.fixture(scope="function")
def db_session():
    # Пересоздаём все таблицы перед каждым тестом
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        # Заполняем данные
        populate_products(db)
        populate_roles(db)
        db.commit()
        yield db
    finally:
        db.rollback()
        db.close()