from authentication.firestore_functions import *
from flask import Flask, session, render_template, request, redirect, jsonify, url_for
from jinja2 import TemplateNotFound
from authentication.firestore_authentication import pb, auth
from decouple import config
from authentication import blueprint
from authentication.forms import LoginForm, CreateAccountForm
import os



app = Flask(__name__)
app.secret_key = config("APP_SECRET_KEY")

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        try:
            email = request.form['username']
            password = request.form['password']
            auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            print(session)
            return hello("Ona")

        # Something (user or pass) is not ok
        except:
            return render_template('accounts/login.html',
                                    msg='Wrong email or password',
                                    form=login_form)

    if 'user' in session:
        return rooms()

    return render_template('accounts/login.html', form=login_form)






if __name__ == "__main__":
    app.run()