import asyncio
import logging
import os
from pathlib import Path

import config
from quart import Quart, jsonify, redirect, render_template, request, session, url_for, send_file
from quart_auth import (
    AuthUser,
    QuartAuth,
    Unauthorized,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from quart_session import Session
from services import get_dialog_by_title
from telegram import (
    InteractiveTelegramClient,
    get_telegram_client,
    initialize_telegram_client,
)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Quart(__name__)
app.secret_key = config.QUART_SECRET_KEY
if os.environ.get("DOCKER_ENVIRONMENT"):
    app.config["SESSION_URI"] = "redis://redis:6379"
app.config.update(
    {
        "DATABASE": Path(app.root_path) / config.SQLITE_DATABASE,
        "SESSION_TYPE": "redis",
        "SESSION_COOKIE_DURATION": 86400,
        "QUART_AUTH_COOKIE_SECURE": False,
    }
)
Session(app)
QuartAuth(app)

USERS_LOGINS = {}


@app.get("/")
async def home():
    """Render the home page."""
    logger.info("Accessed home page.")
    return await render_template("home.html")


@app.get("/list-dialogs")
@login_required
async def list_dialogs():
    """List dialogs for the authenticated user."""
    logger.info("List dialogs route accessed.")
    client: InteractiveTelegramClient = await get_telegram_client(
        current_user.auth_id, USERS_LOGINS
    )
    if not client:
        logger.warning("User not authenticated.")
        return await render_template("login.html")
    dialogs = await client.get_dialogs(limit=15)
    dialogs = [dialog.title for dialog in dialogs]
    phone = current_user.auth_id[1:]
    logger.info("Rendered dialogs.html.")
    return await render_template("dialogs.html", dialogs=dialogs, phone=phone)


@app.get("/list-chat-messages")
@login_required
async def list_chat_messages():
    """List chat messages for a selected dialog."""
    logger.info("List chat messages route accessed.")
    dialog_title = request.args.get("uname")
    client: InteractiveTelegramClient = await get_telegram_client(
        current_user.auth_id, USERS_LOGINS
    )
    if not client:
        logger.warning("User not authenticated.")
        return await render_template("login.html")
    # Get chat from all list chats
    dialog = await get_dialog_by_title(client, dialog_title)
    if dialog:
        try:
            messages = await client.get_messages(dialog, limit=50)
            response_messages = []

            for msg in messages:
                sender = await msg.get_sender()
                username = sender.username if sender.username else sender.first_name
                is_self = sender.is_self

                message_info = {
                    "username": username,
                    "is_self": is_self,
                    "message_text": msg.text,
                }

                response_messages.append(message_info)
            logger.info("Rendered messages.html.")
            return await render_template(
                "messages.html", messages=response_messages, dialog_title=dialog_title
            )
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return f"Error fetching messages: {e}"
    else:
        logger.warning("Dialog not found.")
        return "Dialog not found."


@app.route("/send-message/", methods=["GET", "POST"])
async def send_message():
    """Send a message to a user."""
    if request.method == "GET":
        return await render_template("create-message.html")
    elif request.method == "POST":
        try:
            form = await request.form
            message_text = form.get("message_text")
            username = form.get("username")
            phone = form.get("from_phone")
            if not (message_text and username):
                return (
                    "Invalid form data. Ensure message_text and username are provided.",
                    400,
                )

            client: InteractiveTelegramClient = await get_telegram_client(
                current_user.auth_id, USERS_LOGINS
            )
            if client:
                client.disconnect()
            client = await initialize_telegram_client(phone)
            if not client:
                return jsonify({"status": "Error during login"})
            # Sending the message
            await client.send_message(username, message_text)

            return "Message sent successfully!"
        except Exception as e:
            return f"Error sending message: {e}", 500


@app.route("/login/", methods=["GET", "POST"])
async def login():
    """Handle user login."""
    if request.method == "POST":
        form = await request.form
        phone = form["phone"]
        client: InteractiveTelegramClient = await get_telegram_client(
            current_user.auth_id, USERS_LOGINS
        )
        if not client:
            # Initialize the Telegram client
            client: InteractiveTelegramClient = await initialize_telegram_client(phone)

        if client:
            login_user(AuthUser(phone))
            USERS_LOGINS[phone] = client
            data = None
            if session.get(phone):
                data = {"qr_login_url": session[phone]["qr_link_url"]}
            return await render_template("success_login.html", data=data)
        else:
            data = {"error": "Error during login"}
            return await render_template("login.html", data=data)
    else:
        return await render_template("login.html")


@app.route("/check/login", methods=["GET"])
async def check_login():
    """Check the login status for a user."""
    # Get the phone number from the query parameters
    if not request.args.get("phone"):
        phone = current_user.auth_id
    else:
        phone = "+" + request.args.get("phone")
    # Check if the phone number exists in the dictionary
    if phone in session:
        # Retrieve the login status for the given phone number
        status = session[phone]["status"]
        data = {"status": status}
    else:
        data = {"status": "error", "message": "Phone number not found"}
    return await render_template("check-login.html", data=data)


@app.route("/logout")
async def logout():
    """Handle user logout."""
    try:
        client: InteractiveTelegramClient = await get_telegram_client(
            current_user.auth_id, USERS_LOGINS
        )
        if client:
            client.disconnect()
    except KeyError:
        pass
    logout_user()
    return await render_template("home.html")


@app.errorhandler(Unauthorized)
async def redirect_to_login(*_):
    """Redirect unauthorized users to the login page."""
    return redirect(url_for("login"))


async def main():
    """Run the Quart application."""
    await asyncio.gather(app.run_task(host='0.0.0.0', debug=True))


if __name__ == "__main__":
    asyncio.run(main())
