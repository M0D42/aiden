import os
from flask import Flask
from multiprocessing import Process
from aibot import aiden  # your function

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    # Start Discord bot in separate process
    bot_process = Process(target=aiden)
    bot_process.start()

    # Run Flask webserver
    app.run(host="0.0.0.0", port=port)

    bot_process.join()
