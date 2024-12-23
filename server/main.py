from fastapi import FastAPI, Depends, HTTPException
from auth import register_user, authenticate_user, get_current_user, get_all_users
from news import create_news, get_news, delete_news
from tasks import create_task, get_user_tasks, delete_task
from sqlalchemy.orm import Session
from database import get_db
from models import ChatMessageCreate, ChatMessageRead, create_employee, get_employees, EmployeeCreate, create_event, get_events, EventCreate, UserCreate, UserLogin, TaskCreate, NewsCreate
from database import Base, engine, get_db
from analytics import log_user_activity, generate_activity_report
from datetime import datetime
from chat_service import send_message, get_chat_messages, get_user_chats
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Держи в курсе API",
    description="""
    API для управления данными приложения Держи в курсе.
    Рзработано студентами 3 курса ИПИТ Винтерголлер Тимофеем и Сорокиной Александрой.
    """,
    version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все Origins
    allow_credentials=True,  # Разрешаем передачу cookies через CORS
    allow_methods=["*"],  # Разрешаем все HTTP-методы
    allow_headers=["*"],  # Разрешаем все заголовки
)
# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

# Эндпоинты

# Логирование действия пользователя
@app.post("/log-activity/", tags=["Activity"], description="Регистрация акта активности пользователя.") 
def log_activity(action: str, details: str = None, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    log_user_activity(db, user_id=user.id, action=action, details=details)
    return {"message": "Действие записано"}

# Генерация отчета
@app.get("/activity-report/", tags=["Activity"], description="Вывод отчета активности пользователей с фильтрацией по датам.")
def activity_report(start_date: str, end_date: str, db: Session = Depends(get_db)):
    start_date = datetime.fromisoformat(start_date)
    end_date = datetime.fromisoformat(end_date)
    report = generate_activity_report(db, start_date, end_date)
    return report

@app.post("/employees/", tags=["Employees"], description="Добавление нового сотрудника.", response_model=dict)
def add_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    new_employee = create_employee(db, employee)
    return {"status": "success", "data": {"id": new_employee.id, "name": new_employee.name}}


@app.get("/employees/", tags=["Employees"], description="Вывод всех сотрудников с возможностью фильтрации.")
def list_employees(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    employees = get_employees(db, skip=skip, limit=limit)
    return {"status": "success", "data": employees}


@app.post("/events/", tags=["Events"], description="Добавление нового события.", response_model=dict)
def add_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = create_event(db, event)
    return {"status": "success", "data": {"id": new_event.id, "title": new_event.title}}


@app.get("/events/", tags=["Events"], description="Вывод всех событий с возможностью фильтрации.")
def list_events(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    events = get_events(db, skip=skip, limit=limit)
    return {"status": "success", "data": events}

# Регистрация пользователя
@app.post("/register/", tags=["User"], description="Добавление нового пользователя.")
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)
# Авторизация пользователя
@app.post("/login/", tags=["User"], description="Авторизация пользователя.")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return authenticate_user(db, user)

@app.get("/all_users/", tags=["User"], description="Вывод всех пользователей.")
def all_users(db: Session = Depends(get_db)):
    return get_all_users(db)

@app.get("/id_user/", tags=["User"], description="Вывод пользователя по ID.")
def id_user(user_id: int = 0, db: Session = Depends(get_db)):
    return get_current_user(user_id, db)

# Работа с новостями
@app.post("/news/", tags=["News"], description="Добавление новой новости.")
def add_news(news: NewsCreate, db: Session = Depends(get_db), user: str = None):
    return create_news(db, news, user)

@app.get("/news/", tags=["News"], description="Вывод всех новостей.")
def list_news(db: Session = Depends(get_db)):
    return get_news(db)

@app.delete("/news/{news_id}/", tags=["News"], description="Удаление новости.")
def remove_news(news_id: int, db: Session = Depends(get_db), user_id: int = None):
    return delete_news(db, news_id, user_id)

# Работа с задачами
@app.post("/tasks/", tags=["Tasks"], description="Добавление нового задания.")
def add_task(task: TaskCreate, db: Session = Depends(get_db), user_id: int = None):
    return create_task(db, task, user_id)

@app.get("/tasks/", tags=["Tasks"], description="Вывод всех заданий по ID пользователя.")
def list_tasks(db: Session = Depends(get_db), user_id: int = None):
    return get_user_tasks(db, user_id)

@app.delete("/tasks/{task_id}/", tags=["Tasks"], description="Удаление задания.")
def remove_task(task_id: int, db: Session = Depends(get_db), user_id: int = None):
    return delete_task(db, task_id, user_id)

@app.post("/messages", response_model=ChatMessageRead, tags=["Chat"], description="Отправка нового сообщения.")
def send_message_endpoint(message: ChatMessageCreate, db: Session = Depends(get_db)):
    new_message = send_message(db, message)
    return new_message


@app.get("/chats/{user1_id}/{user2_id}", response_model=list[ChatMessageRead], tags=["Chat"], description="Получение сообщений между двумя пользователями.")
def get_chat_messages_endpoint(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    messages = get_chat_messages(db, user1_id, user2_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Сообщения не найдены")
    return messages


@app.get("/users/{user_id}/chats", tags=["Chat"], description="Получения списка чатов пользователя.")
def get_user_chats_endpoint(user_id: int, db: Session = Depends(get_db)):
    chats = get_user_chats(db, user_id)
    if not chats:
        raise HTTPException(status_code=404, detail="Чаты не найдены")
    return {"chats_with_users": chats}
