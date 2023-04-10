from flask import Flask, render_template
from authentication.firestore_functions import *

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask heroku atespp"

@app.route('/hello/<name>')
def hello(name=None):
    return render_template('home/hello.html', name=name)

@app.route('/rooms')
def rooms():
    # return render_template('login.html')
    rooms = getRooms()
    return render_template('home/rooms.html', segment='rooms', rooms=rooms)

@app.route('/base')
def login():
    return "test"


if __name__ == "__main__":
    app.run()