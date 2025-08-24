from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Discord bot is ready"

def run():
    port = int(os.environ.get("PORT", 8080))

def keep_alive():
    t = Thread(target=run)
    t.start()