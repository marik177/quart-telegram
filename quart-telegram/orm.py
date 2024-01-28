# Import necessary modules and classes
import config  # Assuming config is a module containing database configuration settings
from models import Base, Chat, ChatMessage, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get the database URL from the configuration
db_url = config.get_database_uri()

# Create a SQLAlchemy engine using the specified database URL
engine = create_engine(db_url)

# Create the database tables based on the models
Base.metadata.create_all(engine)

# Create a session factory to interact with the database
Session = sessionmaker(bind=engine)


def create_or_get_user(session: Session, telegram_id: int, username: str) -> User:
    """
    Create a new User entity or get an existing one based on the Telegram ID.
    """
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        session.commit()
    return user


def create_or_get_chat(session: Session, telegram_id: int, chat_title: str) -> Chat:
    """
    Create a new Chat entity or get an existing one based on the Telegram ID.
    """
    chat = session.query(Chat).filter_by(telegram_id=telegram_id).first()
    if not chat:
        chat = Chat(telegram_id=telegram_id, chat_title=chat_title)
        session.add(chat)
        session.commit()
    return chat


def save_message(
    session: Session, sender: User, chat: Chat, message_text: str
) -> ChatMessage:
    """
    Save a new message to the database with user and chat association.
    """
    new_message = ChatMessage(sender=sender, chat=chat, message_text=message_text)
    session.add(new_message)
    session.commit()
    return new_message
