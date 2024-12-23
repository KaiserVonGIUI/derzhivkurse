from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models import User, UserCreate, UserLogin
import hashlib
import os
from database import get_db

# Хэширование пароля
def hash_password(password: str) -> str:
    salt = os.urandom(16)  # Генерация случайной соли
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, 100000
    )
    return salt.hex() + ":" + hashed_password.hex()

# Проверка пароля
def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt, hashed_password = stored_password.split(":")
        new_hashed_password = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), 100000
        )
        return hashed_password == new_hashed_password.hex()
    except Exception:
        return False

# Регистрация пользователя
def register_user(db: Session, user: UserCreate):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Пользователь успешно зарегистрирован"}

# Авторизация пользователя
def authenticate_user(db: Session, user: UserLogin):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Некорректный email или пароль")
    return {"user_id": db_user.id, "user_role": db_user.role}

# Функция для получения текущего пользователя по ID
def get_current_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

def get_all_users(db: Session):
    users = db.query(User).all()
    return [{"id": user.id, "email": user.email, "role": user.role} for user in users]