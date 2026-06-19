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
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_states (
        chat_id TEXT PRIMARY KEY,
        step TEXT
    )
    """)

    conn.commit()
    conn.close()


def set_state(chat_id, step):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO user_states(chat_id, step)
        VALUES (?,?)
        """,
        (str(chat_id), step)
    )

    conn.commit()
    conn.close()


def get_state(chat_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT step FROM user_states
        WHERE chat_id=?
        """,
        (str(chat_id),)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None


def save_user(chat_id, fullname, phone, source):

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users(chat_id, fullname, phone, source)
        VALUES (?,?,?,?)
        """,
        (
            str(chat_id),
            fullname,
            phone,
            source
        )
    )

    conn.commit()
    conn.close()


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

    print("=== BALE RESPONSE ===")
    print(response.text)

    try:
    print("MESSAGE ID =", response.json()["result"]["message_id"])
    return response.json()
except:
    return None


# ---------------- KEYBOARDS ----------------


def main_menu():

    return {
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


def phone_keyboard():

    return {
        "keyboard": [
            [
                {
                    "text": "📱 ارسال شماره تماس",
                    "request_contact": True
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    # ---------------- WEBHOOK ----------------


@app.route("/")
def home():
    return "Webhook Ready"



@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("=== NEW UPDATE ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))


    # دکمه ثبت اطلاعات تماس
    if "callback_query" in data:

        callback = data["callback_query"]

        if callback.get("data") == "register":

            chat_id = callback["from"]["id"]

            set_state(chat_id, "fullname")

            send_message(
                chat_id,
                "لطفاً نام و نام خانوادگی خود را وارد کنید:"
            )

            return "OK", 200



    # دریافت پیام کاربر

    if "message" in data:

        message = data["message"]

        chat = message.get("chat", {})

        chat_id = chat.get("id")

        chat_type = chat.get("type")


        if chat_type != "channel":


            state = get_state(chat_id)



            # مرحله نام و نام خانوادگی

            if state == "fullname":

                fullname = message.get("text", "")


                conn = sqlite3.connect("bot.db")
                cursor = conn.cursor()


                cursor.execute(
                    """
                    INSERT INTO users(chat_id, fullname)
                    VALUES (?,?)
                    """,
                    (
                        str(chat_id),
                        fullname
                    )
                )


                conn.commit()
                conn.close()



                set_state(chat_id, "phone")


                send_message(
                    chat_id,
                    "لطفاً شماره تماس خود را ارسال کنید:",
                    phone_keyboard()
                )


                return "OK", 200




            # مرحله شماره تماس

            if state == "phone":


                contact = message.get("contact")


                if contact:


                    phone = contact.get("phone_number")


                    conn = sqlite3.connect("bot.db")
                    cursor = conn.cursor()


                    cursor.execute(
                        """
                        UPDATE users
                        SET phone=?
                        WHERE chat_id=?
                        """,
                        (
                            phone,
                            str(chat_id)
                        )
                    )


                    conn.commit()
                    conn.close()



                    set_state(chat_id, "source")


                    send_message(
                        chat_id,
                        "از کجا با ما آشنا شدید؟"
                    )


                    return "OK", 200




            # مرحله منبع آشنایی

            if state == "source":


                source = message.get("text", "")


                conn = sqlite3.connect("bot.db")
                cursor = conn.cursor()


                cursor.execute(
                    """
                    UPDATE users
                    SET source=?
                    WHERE chat_id=?
                    """,
                    (
                        source,
                        str(chat_id)
                    )
                )


                conn.commit()
                conn.close()



                set_state(chat_id, None)



                send_message(
                    chat_id,
                    "✅ اطلاعات شما با موفقیت ثبت شد.",
                    main_menu()
                )


                return "OK", 200




            # اگر کاربر فرم فعال نداشت

            send_message(
                chat_id,
                "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                main_menu()
            )


    return "OK", 200




# ساخت دیتابیس

init_db()



if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
