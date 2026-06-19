from flask import Flask, request
import json
import os
import requests
import sqlite3

app = Flask(__name__)

TOKEN = os.environ.get("BALE_TOKEN")


def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        fullname TEXT,
        phone TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return "Webhook Ready"


def send_message(chat_id, text):

    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    requests.post(url, json=payload)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("=== NEW UPDATE ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # کلیک روی دکمه ثبت اطلاعات
    if "callback_query" in data:

        callback = data["callback_query"]

        if callback.get("data") == "register":

            chat_id = callback["from"]["id"]

            send_message(
                chat_id,
                "لطفاً نام و نام خانوادگی خود را وارد کنید:"
            )

            return "OK", 200

    # اگر پیام خصوصی بود
    if "message" in data:
        message = data["message"]

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        chat_type = chat.get("type")

        if chat_type != "channel":
            send_menu(chat_id)

    return "OK", 200


def send_menu(chat_id):

    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "👤 ارتباط با ادمین",
                    "url": "https://ble.ir/seiedghasemtaffakh"
                }
            ],
            [
                {
                    "text": "📝 ثبت اطلاعات تماس",
                    "callback_data": "register"
                }
            ]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
        "reply_markup": keyboard
    }

    requests.post(url, json=payload)


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
