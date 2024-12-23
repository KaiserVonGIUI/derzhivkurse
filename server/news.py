from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import News, NewsCreate

def create_news(db: Session, news: NewsCreate, user_id: int):
    new_news = News(**news.dict(), created_by=user_id)
    db.add(new_news)
    db.commit()
    db.refresh(new_news)
    return new_news

def get_news(db: Session):
    return db.query(News).order_by(News.created_at.desc()).all()

def delete_news(db: Session, news_id: int, user_id: int):
    news = db.query(News).filter(News.id == news_id).first()
    if not news or news.created_by != user_id:
        raise HTTPException(status_code=404, detail="Новость не найдена или доступ запрещен")
    db.delete(news)
    db.commit()
    return {"status": "success"}
