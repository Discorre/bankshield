from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import uuid, jwt, datetime, uvicorn

# ==============================
# Конфигурация базы данных
# ==============================

DATABASE_URL = "postgresql+psycopg2://discorre1:0412@db:5432/bankshield"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==============================
# Определение моделей ORM
# ==============================
class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    full_description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image = Column(String, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    basket_items = relationship("BasketItem", back_populates="user", cascade="all, delete-orphan")

class BasketItem(Base):
    __tablename__ = "basket_items"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    full_description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image = Column(String, nullable=True)
    user = relationship("User", back_populates="basket_items")
    product = relationship("Product")

# Создаем таблицы, если они не существуют
Base.metadata.create_all(bind=engine)

# ==============================
# Схемы (Pydantic модели)
# ==============================
class ProductSchema(BaseModel):
    id: str = None
    name: str
    description: str
    full_description: str = None
    price: float
    image: str = None

    class Config:
        orm_mode = True

class UserSchema(BaseModel):
    id: str
    username: str
    email: str

    class Config:
        from_attributes = True

class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

class ChangePasswordData(BaseModel):
    email: str
    old_password: str
    new_password: str

class BasketItemSchema(BaseModel):
    id: str = None
    user_id: str = None
    product_id: str
    name: str
    description: str
    full_description: str = None
    price: float
    image: str = None

    class Config:
        orm_mode = True

# ==============================
# Конфигурация JWT
# ==============================
SECRET_KEY = "very-sicret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==============================
# Зависимость для получения сессии БД
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==============================
# Создание приложения FastAPI
# ==============================
app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Заполнение базы данных дефолтными продуктами
# ==============================
def populate_products(db: Session):
    default_products = [
        {
            "name": "Мониторинг угроз",
            "description": "Непрерывное наблюдение за инцидентами.",
            "full_description": "Мониторинг угроз – это комплексное наблюдение за потенциальными инцидентами в режиме реального времени. Мы используем современные методы анализа и обнаружения, чтобы своевременно реагировать на возможные атаки и предотвращать ущерб.",
            "price": 20000.0,
            "image": ""
        },
        {
            "name": "Защита платежных систем",
            "description": "Безопасность транзакций.",
            "full_description": "Защита платежных систем включает в себя многоуровневые меры безопасности для защиты транзакций, предотвращения мошеннических атак и обеспечения безопасности финансовых операций. Наши решения адаптируются к современным угрозам.",
            "price": 30000.0,
            "image": ""
        },
        {
            "name": "Анализ уязвимостей",
            "description": "Аудит и выявление слабых мест.",
            "full_description": "Анализ уязвимостей представляет собой комплексный аудит систем банка для выявления слабых мест и уязвимых точек. Наши специалисты предоставят подробный отчёт с рекомендациями по устранению проблем и повышению безопасности.",
            "price": 40000.0,
            "image": ""
        },
        {
            "name": "Инцидентный ответ",
            "description": "Быстрое реагирование на атаки.",
            "full_description": "Инцидентный ответ – это оперативное реагирование на кибератаки с целью минимизации ущерба. Наша команда экспертов быстро восстанавливает системы и предотвращает дальнейшее проникновение злоумышленников.",
            "price": 35000.0,
            "image": ""
        },
        {
            "name": "Криптографическая защита",
            "description": "Современные методы шифрования.",
            "full_description": "Криптографическая защита обеспечивает высокий уровень безопасности данных за счёт применения современных методов шифрования. Мы гарантируем, что ваши данные остаются защищёнными от несанкционированного доступа.",
            "price": 25000.0,
            "image": ""
        },
        {
            "name": "Обучение персонала",
            "description": "Тренинги по кибербезопасности.",
            "full_description": "Обучение персонала включает профессиональные тренинги и семинары, направленные на повышение осведомлённости сотрудников о современных киберугрозах. Мы помогаем формировать культуру безопасности внутри компании.",
            "price": 50000.0,
            "image": ""
        },
    ]
    for prod in default_products:
        exists = db.query(Product).filter(Product.name == prod["name"]).first()
        if not exists:
            new_prod = Product(**prod)
            db.add(new_prod)
    db.commit()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    populate_products(db)
    db.close()

# ==============================
# Эндпоинты для продуктов
# ==============================
@app.get("/products", response_model=list[ProductSchema])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

@app.get("/products/{product_id}", response_model=ProductSchema)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return product

@app.post("/products", response_model=ProductSchema)
def add_product(product: ProductSchema, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/products/{product_id}", response_model=ProductSchema)
def update_product(product_id: str, product: ProductSchema, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    db.delete(db_product)
    db.commit()
    return {"detail": "Продукт удалён"}

# ==============================
# Эндпоинты для пользователей (регистрация, логин)
# ==============================
@app.post("/register", response_model=dict)
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    #access_token = create_access_token(data={"sub": db_user.email})
    return {"message": "Регистрация прошла успешно"}#, "user": UserSchema.from_orm(db_user)}#, "access_token": access_token}

@app.post("/login", response_model=dict)
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.password == data.password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверные данные для входа")
    access_token = create_access_token(data={"sub": user.email})
    return {"message": "Вход выполнен успешно", "access_token": access_token, "user": UserSchema.from_orm(user)}

# ==============================
# Эндпоинт для смены пароля
# ==============================
@app.patch("/change_password")
def change_password(data: ChangePasswordData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.password != data.old_password:
        raise HTTPException(status_code=400, detail="Старый пароль неверный")
    user.password = data.new_password
    db.commit()
    return {"message": "Пароль успешно изменён"}

# ==============================
# Эндпоинты для работы с корзиной
# ==============================
@app.get("/basket/{user_id}", response_model=list[BasketItemSchema])
def get_basket(user_id: str, db: Session = Depends(get_db)):
    items = db.query(BasketItem).filter(BasketItem.user_id == user_id).all()
    return items

@app.post("/basket/{user_id}", response_model=BasketItemSchema)
def add_to_basket(user_id: str, item: BasketItemSchema, db: Session = Depends(get_db)):
    # Проверка: если товар уже добавлен, вернуть ошибку
    existing = db.query(BasketItem).filter(
        BasketItem.user_id == user_id,
        BasketItem.product_id == item.product_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Товар уже добавлен в корзину")
    basket_item = BasketItem(user_id=user_id, **item.dict(exclude_unset=True))
    db.add(basket_item)
    db.commit()
    db.refresh(basket_item)
    return basket_item

@app.delete("/basket/{user_id}/{basket_item_id}")
def delete_from_basket(user_id: str, basket_item_id: str, db: Session = Depends(get_db)):
    print(basket_item_id)
    # Получаем элемент корзины по его первичному ключу
    item = db.query(BasketItem).get(basket_item_id)
    # Если элемент не найден или не принадлежит данному пользователю, возвращаем ошибку
    if not item or item.user_id != user_id:
        raise HTTPException(status_code=404, detail="Элемент корзины не найден")
    db.delete(item)
    db.commit()
    return {"message": "Элемент корзины удалён"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
