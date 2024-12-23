from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import ChatMessage
from models import ChatMessageCreate


def send_message(db: Session, message_data: ChatMessageCreate):
    """
    Сохранение нового сообщения в базе данных.
    """
    new_message = ChatMessage(
        text=message_data.text,
        sender_id=message_data.sender_id,
        receiver_id=message_data.receiver_id,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def get_chat_messages(db: Session, user1_id: int, user2_id: int):
    """
    Получение сообщений между двумя пользователями.
    """
    messages = db.query(ChatMessage).filter(
        or_(
            (ChatMessage.sender_id == user1_id) & (ChatMessage.receiver_id == user2_id),
            (ChatMessage.sender_id == user2_id) & (ChatMessage.receiver_id == user1_id),
        )
    ).order_by(ChatMessage.timestamp.asc()).all()

    return messages


def get_user_chats(db: Session, user_id: int):
    """
    Получение списка уникальных чатов для пользователя.
    """
    messages = db.query(ChatMessage).filter(
        or_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == user_id)
    ).all()

    unique_chats = set()
    for msg in messages:
        if msg.sender_id != user_id:
            unique_chats.add(msg.sender_id)
        if msg.receiver_id != user_id:
            unique_chats.add(msg.receiver_id)

    return list(unique_chats)
