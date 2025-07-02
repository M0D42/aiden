import os
import threading
from flask import Flask
from aibot import aiden  # your bot function

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Im alive'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    # Start Discord bot in a daemon thread so it won't block Flask shutdown
    def start_bot():
        try:
            print("Starting Aiden bot thread...")
            aiden()
        except Exception as e:
            print(f"Aiden bot error: {e}")

    threading.Thread(target=start_bot, daemon=True).start()

    # Run Flask app listening on all interfaces on the assigned port
    app.run(host='0.0.0.0', port=port)
