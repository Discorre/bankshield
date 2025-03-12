from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv, os, uuid, jwt, datetime

# Секретный ключ и алгоритм для JWT
SECRET_KEY = "your-secret-key"  # Замените на более сложный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Разрешаем CORS для фронтенда
origins = ["http://localhost:3000", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Пути к CSV файлам
PRODUCTS_CSV = "products.csv"
USERS_CSV = "users.csv"

# Дефолтный список услуг с подробными описаниями
DEFAULT_PRODUCTS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Мониторинг угроз",
        "description": "Непрерывное наблюдение за инцидентами.",
        "full_description": "Мониторинг угроз – это комплексное наблюдение за потенциальными инцидентами в режиме реального времени. Мы используем современные методы анализа и обнаружения, чтобы своевременно реагировать на возможные атаки и предотвращать ущерб.",
        "price": 200.0,
        "image": ""
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Защита платежных систем",
        "description": "Безопасность транзакций.",
        "full_description": "Защита платежных систем включает в себя многоуровневые меры безопасности для защиты транзакций, предотвращения мошеннических атак и обеспечения безопасности финансовых операций. Наши решения адаптируются к современным угрозам.",
        "price": 300.0,
        "image": ""
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Анализ уязвимостей",
        "description": "Аудит и выявление слабых мест.",
        "full_description": "Анализ уязвимостей представляет собой комплексный аудит систем банка для выявления слабых мест и уязвимых точек. Наши специалисты предоставят подробный отчёт с рекомендациями по устранению проблем и повышению безопасности.",
        "price": 400.0,
        "image": ""
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Инцидентный ответ",
        "description": "Быстрое реагирование на атаки.",
        "full_description": "Инцидентный ответ – это оперативное реагирование на кибератаки с целью минимизации ущерба. Наша команда экспертов быстро восстанавливает системы и предотвращает дальнейшее проникновение злоумышленников.",
        "price": 350.0,
        "image": ""
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Криптографическая защита",
        "description": "Современные методы шифрования.",
        "full_description": "Криптографическая защита обеспечивает высокий уровень безопасности данных за счёт применения современных методов шифрования. Мы гарантируем, что ваши данные остаются защищёнными от несанкционированного доступа.",
        "price": 250.0,
        "image": ""
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Обучение персонала",
        "description": "Тренинги по кибербезопасности.",
        "full_description": "Обучение персонала включает профессиональные тренинги и семинары, направленные на повышение осведомлённости сотрудников о современных киберугрозах. Мы помогаем формировать культуру безопасности внутри компании.",
        "price": 500.0,
        "image": ""
    },
]

# Функция инициализации CSV для продуктов
def initialize_products_csv():
    need_init = False
    if not os.path.exists(PRODUCTS_CSV):
        need_init = True
    else:
        try:
            with open(PRODUCTS_CSV, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None or len(list(reader)) == 0:
                    need_init = True
        except Exception:
            need_init = True

    if need_init:
        with open(PRODUCTS_CSV, mode="w", newline="", encoding="utf-8") as f:
            fieldnames = ["id", "name", "description", "full_description", "price", "image"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for product in DEFAULT_PRODUCTS:
                writer.writerow(product)

def initialize_users_csv():
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, mode="w", newline="", encoding="utf-8") as f:
            fieldnames = ["id", "username", "email", "password"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

initialize_products_csv()
initialize_users_csv()

# Модель продукта с дополнительным полем
class Product(BaseModel):
    id: str = None
    name: str
    description: str
    full_description: str = None
    price: float
    image: str = None

class User(BaseModel):
    id: str = None
    username: str
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def read_products():
    products = []
    with open(PRODUCTS_CSV, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["price"] = float(row["price"])
            except ValueError:
                row["price"] = 0.0
            products.append(row)
    return products

def write_products(products):
    with open(PRODUCTS_CSV, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "name", "description", "full_description", "price", "image"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            writer.writerow(p)

def read_users():
    users = []
    with open(USERS_CSV, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    return users

def write_users(users):
    with open(USERS_CSV, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "username", "email", "password"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for u in users:
            writer.writerow(u)

@app.get("/products")
def get_products():
    return read_products()

@app.get("/products/{product_id}")
def get_product(product_id: str):
    for product in read_products():
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Продукт не найден")

@app.post("/products")
def add_product(product: Product):
    products = read_products()
    product.id = str(uuid.uuid4())
    products.append(product.dict())
    write_products(products)
    return product.dict()

@app.put("/products/{product_id}")
def update_product(product_id: str, product: Product):
    products = read_products()
    for idx, p in enumerate(products):
        if p["id"] == product_id:
            product.id = product_id
            products[idx] = product.dict()
            write_products(products)
            return product.dict()
    raise HTTPException(status_code=404, detail="Продукт не найден")

@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    products = read_products()
    new_products = [p for p in products if p["id"] != product_id]
    if len(new_products) == len(products):
        raise HTTPException(status_code=404, detail="Продукт не найден")
    write_products(new_products)
    return {"detail": "Продукт удалён"}

@app.post("/register")
def register(user: User):
    users = read_users()
    for u in users:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Пользователь уже существует")
    user.id = str(uuid.uuid4())
    users.append(user.dict())
    write_users(users)
    access_token = create_access_token(data={"sub": user.email})
    return {"message": "Регистрация прошла успешно", "user": user.dict(), "access_token": access_token}

@app.post("/login")
def login(data: LoginData):
    for u in read_users():
        if u["email"] == data.email and u["password"] == data.password:
            access_token = create_access_token(data={"sub": u["email"]})
            return {"message": "Вход выполнен успешно", "access_token": access_token, "user": u}
    raise HTTPException(status_code=401, detail="Неверные данные для входа")
