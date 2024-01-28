from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class ChatMessage(Base):
    """
    Model representing chat messages.
    """

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    message_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship with Chat
    chat = relationship("Chat", back_populates="messages")

    # Relationship with User
    sender = relationship("User", back_populates="sent_messages")


class User(Base):
    """
    Model representing users.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String, nullable=True)

    # Relationship with ChatMessage
    sent_messages = relationship("ChatMessage", back_populates="sender")


class Chat(Base):
    """
    Model representing chats.
    """

    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    chat_title = Column(String, nullable=True)

    # Relationship with ChatMessage
    messages = relationship("ChatMessage", back_populates="chat")
