from authentication.firestore_functions import *
from flask import Flask, session, render_template, request, redirect, url_for
from jinja2 import TemplateNotFound
from authentication.firestore_authentication import auth
from decouple import config
from authentication.forms import LoginForm

app = Flask(__name__)
app.secret_key = config("APP_SECRET_KEY")

@app.route('/')
def home():
    return redirect(url_for('rooms'))

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
        return redirect(url_for('login'))


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
        return redirect(url_for('login'))


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
        return redirect(url_for('login'))



@app.route('/room-detail/<scheme_id>/delete-scheme', methods=['GET', 'POST'])
def scheme_delete(scheme_id):
    if 'user' in session:
        try:
            deleteScheme(scheme_id)
            return rooms()
        except:
            return rooms()
    else:
        return redirect(url_for('login'))


def add_user_to_group(request, type):
    try:
        groupid = request.form.get('selectGroup')
        userid = request.form.get('useridentifier')
        addUserToGroup(userid, groupid)
        return redirect(url_for('group', group_id=groupid))
    except:
        return redirect(url_for('user_types', type=type))


@app.route('/users/<type>', methods=['GET', 'POST'])
def user_types(type):
    if 'user' in session:
        data = None
        if request.method == 'POST':
            return add_user_to_group(request, type)
        if type == "All":
            data = getUsers()
        if type == "Students":
            data = getStudents()
        elif type == "Teachers":
            data = getTeachers()
        groups = getNonDefaultGroups()
        if data is not None:
            print(data)

            return render_template('home/users.html', segment='users', type=type, data=data, groups=groups)
    else:
        return redirect(url_for('login'))



@app.route('/users/<type>/see-all', methods=['GET', 'POST'])
def user_pagination(type):
    if 'user' in session:
        data = None
        if request.method == 'POST':
            return add_user_to_group(request, type)

        if type == "All":
            data = getUsers(all=True)
        if type == "Students":
            data = getStudents(all=True)
        elif type == "Teachers":
            data = getTeachers(all=True)

        groups = getNonDefaultGroups()
        if data is not None:
            print("aaaa")

            return render_template('home/users.html', segment='users', type=type, data=data, groups=groups)
    else:
        return redirect(url_for('login'))



@app.route('/users/<type>/<filter_by>/<sort>', methods=['GET', 'POST'])
def user_filtering(type, filter_by, sort):
    if 'user' in session:
        data = None
        if request.method == 'POST':
            return add_user_to_group(request, type)

        if type == "All":
            data = getUsers(filterby=filter_by, sort=sort)
        if type == "Students":
            data = getStudents(filterby=filter_by, sort=sort)
        elif type == "Teachers":
            data = getTeachers(filterby=filter_by, sort=sort)

        groups = getNonDefaultGroups()
        if data is not None:
            print("aaaa")

            return render_template('home/users.html', segment='users', type=type, data=data, groups=groups, sort=sort, filter_by=filter_by)
    else:
        return redirect(url_for('login'))



@app.route('/users/<type>/<filter_by>/<sort>/see-all', methods=['GET', 'POST'])
def user_filtering_all(type, filter_by, sort):
    if 'user' in session:
        if request.method == 'POST':
            return add_user_to_group(request, type)

        data = None

        if type == "All":
            data = getUsers(filterby=filter_by, sort=sort, all=True)
        if type == "Students":
            data = getStudents(filterby=filter_by, sort=sort, all=True)
        elif type == "Teachers":
            data = getTeachers(filterby=filter_by, sort=sort, all=True)

        groups = getNonDefaultGroups()
        if data is not None:
            print("aaaa")

            return render_template('home/users.html', segment='users', type=type, data=data, groups=groups)
    else:
        return redirect(url_for('login'))



@app.route('/users/<user_id>/add-to-group', methods=['GET', 'POST'])
def user_to_group(user_id):
    if 'user' in session:
        if request.method == 'POST':
            print("yes")
            groupid = request.form.get('selectGroup')
            addUserToGroup(user_id, groupid)
            return group(groupid)
        else:
            print("no")
            return user_types("All")
    else:
        return redirect(url_for('login'))


@app.route('/groups', methods=['GET', 'POST'])
def groups():
    if 'user' in session:
        data = getDefaultGroups()
        if data:
            return render_template('home/groups.html', segment='groups', type=type, data=data)
    else:
        return redirect(url_for('login'))



@app.route('/groups/<type>', methods=['GET', 'POST'])
def group_types(type):
    if 'user' in session:
        data = None
        if request.method == 'POST':
            if 'name' in request.form:
                addGroup(request.form['name'])
        if type == "Groups":
            data = getNonDefaultGroups()
        if data is not None:
            return render_template('home/groups.html', segment='groups', type=type, data=data)
    else:
        return redirect(url_for('login'))



@app.route('/group-detail/<group_id>', methods=['GET', 'POST'])
def group(group_id):
    if 'user' in session:
        if request.method == 'POST': #and request.form['useridentifier'] is None:
            room_id = request.form.get('selectGroup')
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
        schemes, dict = getGroupById(group_id)
        groupmembers = getUsersByGroup(group_id)
        rooms = getRooms()
        return render_template('home/group-detail.html', segment='group-detail', schemes=schemes, group=dict,
                               groupmembers=groupmembers, days_of_week=days_of_week, rooms=rooms)

    else:
        return redirect(url_for('login'))



@app.route('/group-detail/<group_id>/delete-group', methods=['GET', 'POST'])
def group_delete(group_id):
    if 'user' in session:
        deleteGroup(group_id)
        return group_types("Groups")
    else:
        return redirect(url_for('login'))



@app.route('/group-detail/<group_id>/delete-user/<user_id>', methods=['GET', 'POST'])
def group_delete_user(group_id, user_id):
    if 'user' in session:
        deleteUserFromGroup(group_id, user_id)
        return group(group_id)
    else:
        return redirect(url_for('login'))



@app.route('/history-room/<room_id>', methods=['GET', 'POST'])
def history_room(room_id):
    if 'user' in session:
        data = None
        if room_id:
            data = getHistoryRoom(room_id)
            _, dict, _ = getRoomById(room_id)
        if data is not None:
            return render_template('home/history-room.html', segment='history-room', logs=data, dict=dict)
    else:
        return redirect(url_for('login'))


@app.route('/history-room/<room_id>/see-all', methods=['GET', 'POST'])
def history_room_all(room_id):
    if 'user' in session:
        data = None
        if room_id:
            data = getHistoryRoom(room_id, first=None, all=True)
            _, dict, _ = getRoomById(room_id)
        if data is not None:
            return render_template('home/history-room.html', segment='history-room', logs=data, dict=dict)
    else:
        return redirect(url_for('login'))



@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user' in session:
        if request.method == 'POST':
            editParameters(request.form)
        acc, sec = getParameters()
        return render_template('home/settings.html', segment='settings', acc=acc, sec=sec)
    else:
        return redirect(url_for('login'))



@app.route('/<template>')
def route_template(template):
    if 'user' in session:
        try:
            if not template.endswith('.html'):
                template += '.html'

            # Detect the current page
            segment = get_segment(request)

            # Serve the file (if exists) from app/templates/home/FILE.html
            """if template == "rooms.html":
                doc = general_parameters.document("parameters").get()
                if doc.exists:
                    params = doc.to_dict()
                    return render_template("home/" + template, segment=segment, accuracy="success")
                else:
                    return render_template("home/" + template, segment=segment, accuracy="fail")
            else:
                return render_template("home/" + template, segment=segment, accuracy="not rooms")"""
            return render_template("home/" + template, segment=segment)

        except TemplateNotFound:
            return render_template('home/page-404.html'), 404

        except:
            return render_template('home/page-500.html'), 500
    else:
        return redirect(url_for('login'))



# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


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
            return redirect(url_for('rooms'))

        # Something (user or pass) is not ok
        except:
            return render_template('accounts/login.html',
                                    msg='Wrong email or password',
                                    form=login_form)
    if 'user' in session:
        return redirect(url_for('rooms'))

    return render_template('accounts/login.html', form=login_form)


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()