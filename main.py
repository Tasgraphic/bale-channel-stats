from flask import Flask, request
import json
import os
import requests
import sqlite3

app = Flask(__name__)

TOKEN = os.environ.get("BALE_TOKEN")

# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        fullname TEXT,
        phone TEXT,
        source TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_state (
        chat_id TEXT PRIMARY KEY,
        step TEXT,
        message_id TEXT
    )
    """)

    conn.commit()
    conn.close()


def set_state(chat_id, step, message_id=None):

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO user_state(chat_id, step, message_id)
    VALUES (?,?,?)
    """, (str(chat_id), step, message_id))

    conn.commit()
    conn.close()


def get_state(chat_id):

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT step, message_id FROM user_state
    WHERE chat_id=?
    """, (str(chat_id),))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0], row[1]

    return None, None


# ---------------- BALE API ----------------

def send_message(chat_id, text, keyboard=None):

    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        payload["reply_markup"] = keyboard

    response = requests.post(url, json=payload)
    return response.json()


def edit_message(chat_id, message_id, text, keyboard=None):

    url = f"https://tapi.bale.ai/bot{TOKEN}/editMessageText"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }

    if keyboard:
        payload["reply_markup"] = keyboard

    requests.post(url, json=payload)


# ---------------- KEYBOARDS ----------------

def main_menu():

    return {
        "inline_keyboard": [
            [
                {"text": "👤 ارتباط با ادمین", "url": "https://ble.ir/seiedghasemtaffakh"}
            ],
            [
                {"text": "📝 ثبت اطلاعات", "callback_data": "register"}
            ]
        ]
    }


def phone_keyboard():

    return {
        "keyboard": [
            [
                {"text": "📱 ارسال شماره", "request_contact": True}
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


# ---------------- WEBHOOK ----------------

@app.route("/")
def home():
    return "Bot is running"


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    # ---------------- START FORM ----------------
    if "callback_query" in data:

        callback = data["callback_query"]

        if callback["data"] == "register":

            chat_id = callback["from"]["id"]

            msg = send_message(chat_id, "لطفاً نام و نام خانوادگی خود را وارد کنید:")

            message_id = msg["result"]["message_id"]

            set_state(chat_id, "fullname", message_id)

            return "OK", 200


    # ---------------- MESSAGE HANDLER ----------------

    if "message" in data:

        msg = data["message"]
        chat = msg["chat"]
        chat_id = chat["id"]

        state, message_id = get_state(chat_id)

        # ---------- FULLNAME ----------
        if state == "fullname":

            fullname = msg.get("text")

            conn = sqlite3.connect("bot.db")
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO users(chat_id, fullname)
            VALUES (?,?)
            """, (str(chat_id), fullname))

            conn.commit()
            conn.close()

            set_state(chat_id, "phone", message_id)

            edit_message(chat_id, message_id, "شماره تماس خود را ارسال کنید:", phone_keyboard())

            return "OK", 200


        # ---------- PHONE ----------
        if state == "phone":

            contact = msg.get("contact")

            if contact:

                phone = contact.get("phone_number")

                conn = sqlite3.connect("bot.db")
                cursor = conn.cursor()

                cursor.execute("""
                UPDATE users
                SET phone=?
                WHERE chat_id=?
                """, (phone, str(chat_id)))

                conn.commit()
                conn.close()

                set_state(chat_id, "source", message_id)

                edit_message(chat_id, message_id, "از کجا با ما آشنا شدید؟")

            return "OK", 200


        # ---------- SOURCE ----------
        if state == "source":

            source = msg.get("text")

            conn = sqlite3.connect("bot.db")
            cursor = conn.cursor()

            cursor.execute("""
            UPDATE users
            SET source=?
            WHERE chat_id=?
            """, (source, str(chat_id)))

            conn.commit()
            conn.close()

            set_state(chat_id, None, None)

            edit_message(chat_id, message_id, "✅ اطلاعات شما ثبت شد", main_menu())

            return "OK", 200


init_db()

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
