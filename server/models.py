from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime

# ORM-модели

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="employees")


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    employees = relationship("Employee", back_populates="department")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    responsible_id = Column(Integer, nullable=False)

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # Тип действия (вход, просмотр, добавление)
    timestamp = Column(DateTime, default=datetime.utcnow)  # Время действия
    details = Column(String, nullable=True)  # Дополнительные данные (ID задачи, события и т.д.)

# Pydantic-схемы

class EmployeeCreate(BaseModel):
    name: str
    position: str = None
    department_id: int


class EventCreate(BaseModel):
    title: str
    description: str = None
    start_date: datetime
    end_date: datetime
    responsible_id: int


# CRUD-функции

def create_employee(db, employee: EmployeeCreate):
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def create_event(db, event: EventCreate):
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_employees(db, skip: int = 0, limit: int = 10):
    return db.query(Employee).offset(skip).limit(limit).all()


def get_events(db, skip: int = 0, limit: int = 10):
    return db.query(Event).offset(skip).limit(limit).all()

# Новые модели

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")  # "user" или "admin"

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    priority = Column(String, nullable=True)
    status = Column(String, default="new")  # "new", "in_progress", "completed"
    assigned_to = Column(Integer, nullable=False)

# Новые Pydantic-схемы

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class NewsCreate(BaseModel):
    title: str
    content: str

class TaskCreate(BaseModel):
    title: str
    description: str = None
    due_date: datetime
    priority: str = "medium"

class ChatMessageCreate(BaseModel):
    text: str
    sender_id: int
    receiver_id: int

class ChatMessageRead(BaseModel):
    id: int
    text: str
    sender_id: int
    receiver_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
