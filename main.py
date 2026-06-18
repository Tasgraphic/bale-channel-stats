from flask import Flask
import os
import requests

app = Flask(__name__)

TOKEN = os.environ.get("BALE_TOKEN")

@app.route("/")
def home():
    try:
        url = f"https://tapi.bale.ai/bot{TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        return response.text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
