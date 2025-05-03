from fastapi import FastAPI, HTTPException, Depends, status, Header, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, String, Float, Text, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from jose import jwt, JWTError, ExpiredSignatureError
from redis_client import redis_client
from jose.exceptions import JWTError
from passlib.context import CryptContext
import uuid
from sqlalchemy import DateTime
from datetime import datetime, timedelta
import datetime
import uvicorn
import os
from dotenv import load_dotenv
import json
from pathlib import Path

load_dotenv()

# ==============================
# Конфигурация безопасности
# ==============================
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ==============================
# Конфигурация базы данных
# ==============================

DATABASE_URL = f"{os.getenv('DB_DRIVER')}://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
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

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, token='{self.token}', user_id={self.user_id})>"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    token = Column(String, nullable=True)
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete")
    token_created_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    
    basket_items = relationship("BasketItem", back_populates="user", cascade="all, delete-orphan")

class BasketItem(Base):
    __tablename__ = "basket_items"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    
    user = relationship("User", back_populates="basket_items")
    product = relationship("Product")

class Appeals(Base):
    __tablename__ = "appeals"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username_apeall = Column(String, nullable=False)
    email_apeall = Column(String, nullable=False)
    text_apeall = Column(String, nullable=False)
    creation_date = Column(DateTime, nullable=False)

Base.metadata.create_all(bind=engine)

# ==============================
# Схемы (Pydantic модели)
# ==============================

class GetAllProductsSchema(BaseModel):
    id: str = None
    name: str
    description: str
    price: float

    class Config:
        orm_mode = True        

class GetOneProductSchema(BaseModel):
    id: str = None
    name: str
    full_description: str = None
    price: float

    class Config:
        orm_mode = True

class UserSchema(BaseModel):
    id: str
    username: str
    email: str

    class Config:
        from_attributes = True

class UserLoginSchema(BaseModel):
    username: str

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
    old_password: str
    new_password: str

# class BasketItemSchema(BaseModel):
#     id: str = None
#     product_id: str

#     class Config:
#         orm_mode = True

class GetBasketItemShema(BaseModel):
    basket_id: str
    name: str
    price: float

    class Config:
        from_attributes = True

class AppealRequest(BaseModel):
    username_appeal: str
    email_appeal: str
    text_appeal: str

# ==============================
# Вспомогательные функции
# ==============================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_access_token(user_id: str, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = {"sub": user_id}
    expire = datetime.datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str, expires_days: int = 7):
    to_encode = {"sub": user_id}
    expire = datetime.datetime.utcnow() + timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(SessionLocal)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or user.token != token:
        raise credentials_exception
    return user

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Недействительный токен")
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истёк")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    
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
    file_path = Path(__file__).parent / "products.json"
    
    with open(file_path, "r", encoding="utf-8") as f:
        default_products = json.load(f)

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
@app.get("/api/v1/products", response_model=list[GetAllProductsSchema])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

@app.get("/api/v1/products/{product_id}", response_model=GetOneProductSchema)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return product

# @app.post("/api/v1/products", response_model=ProductSchema)
# def add_product(product: ProductSchema, db: Session = Depends(get_db)):
#     db_product = Product(**product.dict())
#     db.add(db_product)
#     db.commit()
#     db.refresh(db_product)
#     return db_product

# @app.put("/api/v1/products/{product_id}", response_model=ProductSchema)
# def update_product(product_id: str, product: ProductSchema, db: Session = Depends(get_db)):
#     db_product = db.query(Product).filter(Product.id == product_id).first()
#     if not db_product:
#         raise HTTPException(status_code=404, detail="Продукт не найден")
#     for key, value in product.dict().items():
#         setattr(db_product, key, value)
#     db.commit()
#     db.refresh(db_product)
#     return db_product

# @app.delete("/api/v1/products/{product_id}")
# def delete_product(product_id: str, db: Session = Depends(get_db)):
#     db_product = db.query(Product).filter(Product.id == product_id).first()
#     if not db_product:
#         raise HTTPException(status_code=404, detail="Продукт не найден")
#     db.delete(db_product)
#     db.commit()
#     return {"detail": "Продукт удалён"}

# ==============================
# Эндпоинты для пользователей (регистрация, логин)
# ==============================

@app.post("/api/v1/register", response_model=dict)
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
   
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
   

    return { "message": "Регистрация прошла успешно" }

@app.post("/api/v1/login", response_model=dict)
def login(data: LoginData, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные данные для входа")

    token = create_access_token(user.id)

    user.token = token
    user.token_created_at = datetime.datetime.utcnow()
    user.last_login_at = datetime.datetime.utcnow()
    refresh_token = create_refresh_token(str(user.id))

    db.add(RefreshToken(user_id=user.id, token=refresh_token))
    db.commit()

    return {
        "message": "Вход выполнен успешно",
        "access_token": token,
        "refresh_token": refresh_token,
        "user": UserLoginSchema.from_orm(user)
    }

@app.post("/api/v1/refresh")
def refresh_access_token(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(authorization, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        exp = payload.get("exp")

        if not user_id or not exp:
            raise HTTPException(status_code=401, detail="Недействительный токен")

        # Срок действия
        if datetime.datetime.utcfromtimestamp(exp) < datetime.datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh токен истёк")

        # Проверка, существует ли токен в БД
        stored_token = db.query(RefreshToken).filter_by(token=authorization, user_id=user_id).first()
        if not stored_token:
            raise HTTPException(status_code=401, detail="Refresh токен не найден или отозван")

        # Генерация нового access токена
        new_access_token = create_access_token(user_id)
        return {"access_token": new_access_token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный refresh токен")


@app.post("/api/v1/logout")
def logout_user(
    refresh_token: str = Header(...),
    db: Session = Depends(get_db)
):
    token_entry = db.query(RefreshToken).filter_by(token=refresh_token).first()

    if token_entry == None:
        raise HTTPException(status_code=401, detail="Refresh токен говно")

    user = db.query(User).filter_by(id=token_entry.user_id).first()

    user.token = ""
    db.delete(token_entry)
    db.commit()
    db.refresh(user)
    
    return {"message": "Вы вышли из системы"}

# ==============================
# Эндпоинт для смены пароля
# ==============================
@app.patch("/api/v1/change_password")
def change_password(
    data: ChangePasswordData,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Неверная схема авторизации")
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный токен")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Недействительный токен")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    user = db.query(User).filter(User.id == user_id, User.token == token).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден или токен недействителен")

    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Старый пароль неверный")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    return {"message": "Пароль успешно изменён"}

@app.get("/api/v1/basket", response_model=list[GetBasketItemShema])
def get_basket(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Токен доступа обязателен")

    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Возвращаем товары из корзины
    return [
        {
            "basket_id": item.id,
            "name": item.product.name,
            "price": item.product.price
        }
        for item in user.basket_items
    ]

class AddToBasketRequest(BaseModel):
    product_id: str

@app.post("/api/v1/basket")
def add_to_basket(
    item: AddToBasketRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Недействительный токен")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    user = db.query(User).filter(User.id == user_id, User.token == token).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден или токен недействителен")

    existing_item = db.query(BasketItem).filter(
        BasketItem.user_id == user.id,
        BasketItem.product_id == item.product_id
    ).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Товар уже добавлен в корзину")

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    basket_item = BasketItem(
        user_id=user.id,
        product_id=product.id,
    )

    db.add(basket_item)
    db.commit()
    db.refresh(basket_item)

    return basket_item

@app.delete("/api/v1/basket/{basket_item_id}")
def delete_from_basket(
    basket_item_id: str,
    authorization: str = Header(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Токен доступа обязателен")

    # Извлекаем токен из заголовка Authorization
    token = authorization.split(" ")[1]
    
    # Валидация токена
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    item = db.query(BasketItem).get(basket_item_id)
    if not item or item.user_id != user_id:
        raise HTTPException(status_code=404, detail="Элемент корзины не найден")
    
    db.delete(item)
    db.commit()
    return {"message": "Элемент корзины удалён"}

@app.post("/api/v1/appeal")
def add_new_appeal(
    appeal: AppealRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Токен доступа обязателен")

    # Извлекаем токен из заголовка Authorization
    token = authorization.split(" ")[1]
    
    # Валидация токена
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    
    new_appeal = Appeals(
        username_apeall=appeal.username_appeal,
        email_apeall=appeal.email_appeal,
        text_apeall=appeal.text_appeal,
        creation_date=datetime.datetime.utcnow()
    )

    db.add(new_appeal)
    db.commit()
    db.refresh(new_appeal)

    return {"message": "Ваше сообщение будер рассмотрено"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
