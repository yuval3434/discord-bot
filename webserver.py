import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Discord bot is ready"

if __name__ == "__main__":
    port = int(os.environ.get("PORT"))
    app.run(host="0.0.0.0", port=port)