from fastapi import FastAPI, HTTPException, Depends, status, Header, Response, Query, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import CheckConstraint, create_engine, Column, String, Float, Text, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from jose import jwt, JWTError, ExpiredSignatureError
from redis_client import redis_client
from jose.exceptions import JWTError
from passlib.context import CryptContext
import uuid
from sqlalchemy import DateTime
from datetime import timedelta
import datetime
import uvicorn
import os
from dotenv import load_dotenv
import json
from pathlib import Path
import logging
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль
        logging.FileHandler("app.log")  # Запись в файл app.log
    ]
)

logger = logging.getLogger(__name__)

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
    id = Column(String(40), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(55), nullable=False)
    description = Column(Text, nullable=False)
    full_description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image = Column(String, nullable=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(40), ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, token='{self.token}', user_id={self.user_id})>"

class Roles(Base):
    __tablename__ = "roles"
    role_id = Column(String(40), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)

    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(name.in_(['admin', 'user']), name='valid_role_name'),
    )

    def __repr__(self):
        return f"<Roles(name='{self.name}')>"

class User(Base):
    __tablename__ = "users"
    id = Column(String(40), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(55), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    token = Column(String, nullable=True)
    role_id = Column(String(40), ForeignKey("roles.role_id"), nullable=False)
    token_created_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete")
    basket_items = relationship("BasketItem", back_populates="user", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

    def get_role_names(self):
        return [ur.role.name for ur in self.user_roles]
    
class UserRole(Base):
    __tablename__ = "userrole"
    id = Column(String(40), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    role_id = Column(String(40), ForeignKey("roles.role_id"), nullable=False)
    user_id = Column(String(40), ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Roles", back_populates="user_roles")


class BasketItem(Base):
    __tablename__ = "basket_items"
    id = Column(String(40), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(40), ForeignKey("users.id"), nullable=False)
    product_id = Column(String(40), ForeignKey("products.id"), nullable=False)

    user = relationship("User", back_populates="basket_items")
    product = relationship("Product")

class Appeals(Base):
    __tablename__ = "appeals"
    id = Column(String(40), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username_apeall = Column(String(55), nullable=False)
    email_apeall = Column(String(255), nullable=False)
    text_apeall = Column(String, nullable=False)
    creation_date = Column(DateTime, nullable=False)

Base.metadata.create_all(bind=engine)

# ==============================
# Схемы (Pydantic модели)
# ==============================

class UpdateProductsSchema(BaseModel):
    id: str = None
    name: str
    description: str
    full_description: str
    price: float

    class Config:
        orm_mode = True

class GetRole(BaseModel):
    name: str

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
# Зависимость для получения сессии БД
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str, expires_days: int = 7):
    to_encode = {"sub": user_id}
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    if not token:
            raise HTTPException(status_code=401, detail="Токен доступа обязателен")
    if redis_client.exists(token):
        raise HTTPException(status_code=401, detail="Срок действия токена истёк или он был отозван")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Недействительный токен1")
        return user_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истёк")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токенё12")


def get_current_user(authorization: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print("after [ ]: ", authorization)

    token = authorization.split(" ")[1]
    print("before [ ]: ", token)

    user_id = verify_token(token)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or user.token != token:
        raise credentials_exception
    return user
    
def check_roles(required_roles: list[str]):
    def role_checker(user: User = Depends(get_current_user)):
        user_roles = user.get_role_names()
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Недостаточно прав")
        return user
    return role_checker

def has_required_roles(user: User, required_roles: list[str]) -> bool:
    user_roles = user.get_role_names()
    return any(role in user_roles for role in required_roles)

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
    

def populate_roles(db: Session):
    file_path = Path(__file__).parent / "roles.json"

    if not file_path.exists():
        raise FileNotFoundError(f"Файл {file_path} не найден")

    with open(file_path, "r", encoding="utf-8") as f:
        default_roles = json.load(f)

    for role_data in default_roles:
        role_name = role_data.get("name")
        if not role_name:
            raise ValueError("Роль должна содержать поле 'name'")

        existing_role = db.query(Roles).filter(Roles.name == role_name).first()

        if not existing_role:
            new_role = Roles(name=role_name)
            db.add(new_role)

    db.commit()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    populate_products(db)
    populate_roles(db)
    db.close()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP error: {exc.detail} (status_code={exc.status_code}) on {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()} on {request.url}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
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


@app.get("/api/v1/allproducts/{product_id}", response_model=UpdateProductsSchema)
def get_products(product_id : str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    return product


@app.post("/api/v1/products")
def add_product(
    product: UpdateProductsSchema,
    Authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        user = get_current_user(Authorization, db)
        check_roles(["admin"])(user)
    except HTTPException as e:
        raise e

    db_product = Product(**product.dict())

    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при добавлении продукта")
    
    return {"message": f"Данные о продукте \"{db_product.name}\" успешно добавлены"}

@app.patch("/api/v1/products")
def update_product(
    product: UpdateProductsSchema, 
    prod_id: str = Query(..., description="ID продукта для обновления"),
    Authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        user = get_current_user(Authorization, db)
        check_roles(["admin"])(user)
    except HTTPException:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    db_product = db.query(Product).filter(Product.id == prod_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    # Исключаем обновление id
    update_data = product.dict(exclude_unset=True)
    if "id" in update_data:
        del update_data["id"]

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    return {"message": f"Данные продукта \"{db_product.name}\" успешно обновлены"}

@app.delete("/api/v1/products")
def delete_product(
    prod_id: str = Query(..., description="ID продукта для удаления"),
    Authorization: str = Header(...),
    db: Session = Depends(get_db)
):   
    try:
        user = get_current_user(Authorization, db)
        check_roles(["admin"])(user)
    except HTTPException as e:
        raise e
                  
    db_product = db.query(Product).filter(Product.id == prod_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    db.delete(db_product)
    db.commit()
    return {"detail": "Данные продукта успешно удалены"}

# ==============================
# Эндпоинты для пользователей (регистрация, логин)
# ==============================

@app.post("/api/v1/admin/register", response_model=dict)
def register_admin(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    user_role = db.query(Roles).filter(Roles.name == "admin").first()
    if not user_role:
        raise HTTPException(status_code=500, detail="Роль 'admin' не найдена в системе")
   
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role_id=user_role.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    user_role_link = UserRole(
        user_id=db_user.id,
        role_id=user_role.role_id
    )
    db.add(user_role_link)
    db.commit()
   
    return { "message": "Регистрация админа прошла успешно" }

@app.post("/api/v1/admin/login", response_model=dict)
def login_admin(data: LoginData, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные данные для входа")

    is_admin = has_required_roles(user ,["admin"])

    if is_admin != True:
        raise HTTPException(status_code=403, detail="У вас недостаточно прав")

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

@app.post("/api/v1/register", response_model=dict)
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    user_role = db.query(Roles).filter(Roles.name == "user").first()
    if not user_role:
        raise HTTPException(status_code=500, detail="Роль 'user' не найдена в системе")
   
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role_id=user_role.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    user_role_link = UserRole(
        user_id=db_user.id,
        role_id=user_role.role_id
    )
    db.add(user_role_link)
    db.commit()
   
    return { "message": "Регистрация прошла успешно" }

@app.post("/api/v1/login", response_model=dict)
def login(data: LoginData, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные данные для входа")

    is_admin = has_required_roles(user ,["user"])

    if is_admin != True:
        return {"message": "Пожалуйста, используйте правильную форму для регистрации"}

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

@app.get("/api/v1/me")
def get_me(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
    ):

    user = get_current_user(authorization, db)

    return {
        "username": user.username,
        "email": user.email,
        "roles": "admin" if has_required_roles(user ,["admin"]) else "user"
    }

@app.post("/api/v1/refresh")
def refresh_access_token(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        # Парсим и проверяем refresh_token
        payload = jwt.decode(authorization, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        exp = payload.get("exp")

        if not user_id or not exp:
            raise HTTPException(status_code=401, detail="Недействительный токен")

        # Проверка истечения срока действия
        if datetime.datetime.utcfromtimestamp(exp) < datetime.datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh токен истёк")

        # Проверяем, существует ли refresh_token в БД
        stored_token = db.query(RefreshToken).filter_by(token=authorization, user_id=user_id).first()
        if not stored_token:
            raise HTTPException(status_code=401, detail="Refresh токен не найден или отозван")

        # Получаем пользователя из БД
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Генерируем новый access_token
        new_access_token = create_access_token(user_id)

        # Обновляем токен и время в БД
        user.token = new_access_token
        user.token_created_at = datetime.datetime.utcnow()

        # Сохраняем изменения
        db.commit()
        db.refresh(user)

        return {"access_token": new_access_token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный refresh токен")


@app.post("/api/v1/logout")
def logout_user(
    refresh_token: str = Header(...),
    db: Session = Depends(get_db)
):
    token_entry = db.query(RefreshToken).filter_by(token=refresh_token).first()
    if not token_entry:
        raise HTTPException(status_code=401, detail="Неверный refresh токен")

    user = db.query(User).filter_by(id=token_entry.user_id).first()
    current_access_token = user.token

    # Удаление refresh токена
    db.delete(token_entry)

    # Очистка access токена в БД
    user.token = ""

    # Добавление access токена в Redis как "отозванного"
    redis_client.setex(current_access_token, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "revoked")

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

    token = authorization.split(" ")[1]
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

    token = authorization.split(" ")[1]
    
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
