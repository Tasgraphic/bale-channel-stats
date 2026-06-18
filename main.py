from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "Webhook Ready"

@app.route("/webhook", methods=["POST"])
def webhook():
    print("=== NEW UPDATE ===")
    print(json.dumps(request.json, ensure_ascii=False, indent=2))
    return "OK", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
