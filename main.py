from flask import Flask, request
import json
import os
import requests

app = Flask(__name__)

TOKEN = os.environ.get("BALE_TOKEN")


@app.route("/")
def home():
    return "Webhook Ready"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("=== NEW UPDATE ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # اگر پیام خصوصی بود
    if "message" in data:
        message = data["message"]

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        chat_type = chat.get("type")

        if chat_type != "channel":
            send_admin_button(chat_id)

    return "OK", 200


def send_admin_button(chat_id):

    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "👤 ارتباط با ادمین",
                    "url": "https://ble.ir/seiedghasemtaffakh"
                }
            ]
        ]
    }

    payload = {
        "chat_id": chat_id,
        "text": "برای ارتباط با مدیریت روی دکمه زیر کلیک کنید:",
        "reply_markup": keyboard
    }

    requests.post(url, json=payload)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
