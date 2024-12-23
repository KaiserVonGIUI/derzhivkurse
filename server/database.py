from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# URL для подключения к PostgreSQL
DATABASE_URL = "postgresql://postgres:21042005@localhost/drugoedelo"

# Настройка движка и сессии
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
