from flask import Flask
import os
import requests

app = Flask(__name__)

BALE_TOKEN = os.environ.get("BALE_TOKEN")

@app.route("/")
def home():
    if BALE_TOKEN:
        return "Bale Bot Token Loaded"
    else:
        return "Token Not Found"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
