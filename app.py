from flask import Flask
from aibot import aiden
import threading

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Im alive'

# Start the Discord bot in a new thread
threading.Thread(target=aiden).start()
