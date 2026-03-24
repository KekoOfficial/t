from flask import Flask, jsonify
from telegram_bot.downloader import estado_cola

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "cola": estado_cola
    })

app.run(host="0.0.0.0", port=5000)