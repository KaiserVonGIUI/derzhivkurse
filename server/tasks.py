from models import Task, TaskCreate
from fastapi import HTTPException
from sqlalchemy.orm import Session

def create_task(db: Session, task: TaskCreate, user_id: int):
    new_task = Task(**task.dict(), assigned_to=user_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_user_tasks(db: Session, user_id: int):
    return db.query(Task).filter(Task.assigned_to == user_id).all()

def delete_task(db: Session, task_id: int, user_id: int):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена или доступ запрещен")
    db.delete(task)
    db.commit()
    return {"status": "success"}
