import logging

import orm
from botqrcode import QRCodeBot
from config import API_HASH, API_ID
from quart import session
from telethon import TelegramClient, events, utils
from telethon.network import ConnectionTcpAbridged

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractiveTelegramClient(TelegramClient):
    """
    A custom Telegram client class that extends the Telethon library's TelegramClient.
    It includes additional methods for handling user authorization using a QR code.
    """

    def __init__(self, session_user_id, api_id, api_hash, qr=QRCodeBot(), proxy=None):
        """
        Initialize the InteractiveTelegramClient.

        Parameters:
        - session_user_id: The unique identifier for the user's session.
        - api_id: The Telegram API ID.
        - api_hash: The Telegram API hash.
        - qr: An instance of the QRCodeBot class for QR code handling.
        - proxy: Optional proxy configuration for the connection.
        """
        self.phone = session_user_id
        self.qr = qr
        self.qr_code_url = None
        super().__init__(
            session_user_id,
            api_id,
            api_hash,
            connection=ConnectionTcpAbridged,
            proxy=proxy,
        )

    async def initialize(self):
        """
        Asynchronously initialize the Telegram client by connecting to the servers
        and handling user authorization using QR code login.
        """
        await self._connect_or_retry()
        await self._handle_user_authorization()

    async def _connect_or_retry(self):
        """
        Asynchronously attempt to connect to Telegram servers, retrying on initial failure.
        """
        print("Connecting to Telegram servers...")
        try:
            await self.connect()
        except IOError:
            print("Initial connection failed. Retrying...")
            await self.connect()

    async def _handle_user_authorization(self):
        """
        Asynchronously handle user authorization, including QR code login if not already authorized.
        """
        if not await self.is_user_authorized():
            session[self.phone] = {"status": "waiting_qr_login"}
            qr_login = await self.qr_login()
            session[self.phone]["qr_link_url"] = qr_login.url
            self.qr_code_url = qr_login.url
            r = False
            while not r:
                self.qr.display_url_as_qr(qr_login.url)
                try:
                    r = await qr_login.wait()
                    session[self.phone]["status"] = "logined"
                except Exception as e:
                    print(f"Error during QR login: {e}")
                    break


async def initialize_telegram_client(phone: str):
    """
    Asynchronously initialize a Telegram client and return it if the user is authorized.

    Args:
        phone (str): The phone number associated with the Telegram user.

    Returns:
        InteractiveTelegramClient | None: An initialized Telegram client if user authorization
        is successful, or None if there is an issue during initialization or if the user is not
        authorized.
    """
    client = InteractiveTelegramClient(phone, API_ID, API_HASH)
    await client.initialize()
    if await client.is_user_authorized():
        client.add_event_handler(recieve_and_save_new_messages)
        return client
    return client


async def get_telegram_client(phone: str, users_logins: dict):
    """
    Asynchronously retrieve a Telegram client based on the provided phone number.
    """
    return users_logins.get(phone, None)


@events.register(events.NewMessage)
async def recieve_and_save_new_messages(event):
    """
    Event handler for processing and saving new incoming messages to the database.
    """
    sender = await event.get_sender()
    chat = await event.get_chat()

    sender_username = utils.get_display_name(sender)
    sender_telegram_id = sender.id
    chat_title = utils.get_display_name(chat)
    chat_telegram_id = chat.id
    message_text = event.text

    # Get or create the sender and chat users in the database
    db_session = orm.Session()
    sender_user = orm.create_or_get_user(
        db_session, sender_telegram_id, sender_username
    )
    chat_entity = orm.create_or_get_chat(db_session, chat_telegram_id, chat_title)

    # Save the message to the database with user and chat association
    orm.save_message(db_session, sender_user, chat_entity, message_text)

    logger.info(
        f"Saved message from {sender_username} to chat {chat_title}: {message_text}!"
    )
