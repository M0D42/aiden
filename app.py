from flask import Flask
from aibot import aiden
import threading
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Im alive'

if __name__ == "__main__":
    # Avoid running the bot twice with Flask debug reloader
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=aiden).start()
    app.run(host='0.0.0.0', port=5000)
