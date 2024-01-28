import os
import sys
import time

from dotenv import load_dotenv

load_dotenv()


def get_env(name, message, cast=str):
    """Helper to get environment variables interactively"""
    if name in os.environ:
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            time.sleep(1)


def get_database_uri():
    return f"sqlite:///{SQLITE_DATABASE}"


SQLITE_DATABASE = os.getenv("SQLITE_DATABASE", "messages.sqlite")
QUART_SECRET_KEY = os.getenv("QUART_SECRET_KEY")

# Telegram
API_ID = get_env("TG_API_ID", "Enter your API ID: ", int)
API_HASH = get_env("TG_API_HASH", "Enter your API hash: ")
