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


@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if 'user' in session:
        if request.method == 'POST':
            addRoom(request.form['name'], request.form['location'])
        try:
            rooms = getRooms()
            return render_template('home/rooms.html', segment='rooms', rooms=rooms)
        except:
            return render_template('home/rooms.html', segment='rooms', rooms="hey")
    else:
        return login()


@app.route('/room-detail/<room_id>', methods=['GET', 'POST'])
def room(room_id):
    if 'user' in session:
        if request.method == 'POST':
            if 'name' in request.form or 'location' in request.form:
                editRoom(request.form, room_id)
            else:
                group_id = request.form.get('selectGroup')
                schedule_week = {}
                for day in days_of_week:
                    print(day)
                    list = []
                    if request.form[f'input11{day}'] != '' and request.form[f'input12{day}'] != '':
                        listElement = request.form[f'input11{day}'] + " - " + request.form[f'input12{day}']
                        list.append(listElement)
                    if request.form[f'input21{day}'] != '' and request.form[f'input22{day}'] != '':
                        listElement = request.form[f'input21{day}'] + " - " + request.form[f'input22{day}']
                        list.append(listElement)
                    schedule_week[day] = list
                addScheme(schedule_week, group_id, room_id)

        if getRoomById(room_id) and getAllGroups():
            schemes, dict, lastUnlocked = getRoomById(room_id)
            groups = getAllGroups()
            currently_allowed = getCurrentlyAllowed(schemes)
            return render_template('home/room-detail.html', segment='room-detail', room=dict, schemes=schemes,
                                   days_of_week=days_of_week, groups=groups, lastUnlocked=lastUnlocked,
                                   currently_allowed=currently_allowed)
    else:
        return login()


@app.route('/room-detail/<room_id>/<room_action>', methods=['GET', 'POST'])
def room_delete(room_id, room_action):
    if 'user' in session:
        if room_action == "delete-room":
            deleteRoom(room_id)
        elif room_action == "unlock-door":
            unlockRoom(room_id)
            return room(room_id)
        return rooms()
    else:
        return login()


@app.route('/room-detail/<scheme_id>/delete-scheme', methods=['GET', 'POST'])
def scheme_delete(scheme_id):
    if 'user' in session:
        try:
            deleteScheme(scheme_id)
            return rooms()
        except:
            return rooms()
    else:
        return login()


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
            return rooms()

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