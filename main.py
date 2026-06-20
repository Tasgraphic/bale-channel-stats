from flask import Flask
from config import Config
from database import init_database

# ساخت برنامه
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bot.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# تنظیمات
app.config.from_object(Config)


# اتصال دیتابیس
init_database(app)


@app.route("/")
def home():

    return "Bale Analyzer is Running 🚀"



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )