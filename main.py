from flask import Flask, request
import json
import os
import requests

app = Flask(__name__)

TOKEN = os.environ.get("BALE_TOKEN")


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

    return response.json()


# ---------------- KEYBOARD ----------------

def main_menu():

    return {
        "inline_keyboard": [
            [
                {
                    "text": "👤 ارتباط با ادمین",
                    "url": "https://ble.ir/seiedghasemtaffakh"
                }
            ]
        ]
    }


# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return "Bot is running"


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("=== NEW UPDATE ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    try:

        if "message" in data:

            message = data["message"]

            chat = message.get("chat", {})
            chat_id = chat.get("id")

            send_message(
                chat_id,
                "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                main_menu()
            )

        return "OK", 200

    except Exception as e:

        print("ERROR:", e)
        return "OK", 200


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )