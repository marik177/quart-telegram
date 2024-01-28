# Quart Telegram Chat App

This is a simple chat application using Quart and Telethon to interact with the Telegram API.

## Setup

### Prerequisites

- Python 3.7 or higher
- Redis server (for sessions)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/marik177/quart-telegram.git
    cd quart-telegram
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up the environment variables:

    Create a `.env` file in the project root and add the following:

    ```env
    QUART_SECRET_KEY=your_secret_key
    TELEGRAM_API_ID=your_telegram_api_id
    TELEGRAM_API_HASH=your_telegram_api_hash
    SQLITE_DATABASE=messages.sqlite
    ```

    Replace `your_secret_key`, `your_telegram_api_id`, and `your_telegram_api_hash` with your actual values.

4. Run the application:

    ```bash
    hypercorn quart_app.py:app
    ```

## Usage

- Access the application at [http://localhost:5000](http://localhost:5000) in your web browser.
- Log in using your Telegram phone number.
- Start chatting with friends or send messages to yourself.

## Features

- Authentication with Telegram using QR code.
- List and view Telegram dialogs.
- View and send messages within a chat.
