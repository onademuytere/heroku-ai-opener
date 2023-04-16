from authentication.firestore_authentication import db
from datetime import datetime, timedelta
from firebase_admin import firestore

days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


def get_firestore_by_id(collection, col_id, order_by=None):
    doc = db.collection(collection).document(col_id).get()
    col_item = doc.to_dict()
    return col_item


def get_firestore_collection(collection, order_by=None):
    list_collection = []
    docs = db.collection(collection)
    if order_by:
        docs = docs.order_by(order_by)
    docs = docs.stream()
    for doc in docs:
        dict = doc.to_dict()
        dict["id"] = doc.id
        list_collection.append(dict)
    return list_collection


### ROOM FUNCTIONS
def getRooms():
    try:
        return get_firestore_collection("room", order_by="location")
    except:
        return None


def getRoomById(room_id, value=None):
    doc_ref = db.collection(u'room').document(room_id)
    doc = doc_ref.get()
    schemes = []
    if doc.exists:
        dict = doc.to_dict()
        if value == "roomname":
            return dict["roomname"]
        else:
            dict["id"] = room_id
            docs = db.collection(u'scheme').where(u'room_id', u'==', room_id).stream()
            if docs:
                for doc in docs:
                    dict_scheme = doc.to_dict()
                    dict_scheme["id"] = doc.id
                    schemes.append(dict_scheme)
            last_unlocked = getHistoryRoom(room_id, True)
            return schemes, dict, last_unlocked


def addRoom(name, location):
    data = {
        u'roomname': name,
        u'location': location,
        u'unlock': False
    }
    db.collection(u'room').add(data)


def editRoom(req, room_id):
    dict = {}
    if req['name']:
        name = req['name']
        dict['roomname'] = name
    if req['location']:
        location = req['location']
        dict['location'] = location

    room_ref = db.collection(u'room').document(room_id)
    room_ref.update(dict)


def deleteRoom(room_id):
    # first delete the schemes associated with this room
    doc_ref = db.collection(u'scheme').where(u'room_id', u'==', room_id).get()

    if doc_ref:
        batch = db.batch()
        for doc in doc_ref:
            batch.delete(doc.reference)
        batch.commit()

    # delete the room itself
    db.collection(u'room').document(room_id).delete()


def getCurrentlyAllowed(schemes):
    currently_allowed = []
    for scheme in schemes:
        dt = datetime.now()
        current_day = dt.strftime('%A').lower()
        current_time = dt.strftime("%H:%M")

        if scheme[current_day]:
            timeslots = scheme[current_day]
            groupinfo = {"groupid": scheme['assigned_to']}
            groupname = getGroupById(scheme['assigned_to'], value="groupname")
            groupinfo["groupname"] = groupname

            for timeslot in timeslots:
                splitted = timeslot.split(" - ")
                # if current time is in between a time slot
                if splitted[0] <= current_time <= splitted[1]:
                    currently_allowed.append(groupinfo)
    return currently_allowed


def unlockRoom(room_id):
    dict_unlock = {'unlock': True}
    room_ref = db.collection(u'room').document(room_id)
    room_ref.update(dict_unlock)


### USER FUNCTIONS
# All users functions
def getUserById(user_id):
    try:
        return get_firestore_by_id("user", user_id)
    except:
        return None


def getUsersByGroup(group_id):
    users = []
    doc = db.collection(u'user').stream()
    if doc:
        for user in doc:
            dict = user.to_dict()
            for group in dict["group_id"]:
                if group == group_id:
                    dict["id"] = user.id
                    users.append(dict)
        return users
    else:
        return None


def addUserToGroup(userid, groupid):
    data = {
        u'group_id': firestore.ArrayUnion([groupid])
    }
    db.collection(u'user').document(userid).update(data)


def getUsers(filterby=None, sort=None, all=False):
    users = []
    docs = None
    if filterby and sort:
        print(filterby)
        # search in firstnames, lastnames and id
        if all:
            if sort == "asc":
                docs = db.collection(u'user').order_by(filterby).stream()
            else:
                docs = db.collection(u'user').order_by(filterby, direction=firestore.Query.DESCENDING).stream()
        else:
            if sort == "asc":
                docs = db.collection(u'user').order_by(filterby).limit(20).stream()
            else:
                docs = db.collection(u'user').order_by(filterby, direction=firestore.Query.DESCENDING).limit(
                    20).stream()
    elif all:
        docs = db.collection(u'user').order_by(u'lastname').stream()
    else:
        docs = db.collection(u'user').order_by(u'lastname').limit(20).stream()
    if docs:
        for doc in docs:
            dict = doc.to_dict()
            dict["id"] = doc.id
            classname = ""
            if dict["is_teacher"] is False:
                classname = getClassById(dict["class_id"])
            dict["classname"] = classname
            users.append(dict)
        return users

# All students
def getStudents(filterby=None, sort=None, all=False):
    students = []
    docs = None
    if filterby and sort:
        print(filterby)
        # search in firstnames, lastnames and id
        if all:
            if sort == "asc":
                docs = db.collection(u'user').where(u'is_teacher', u'==', False).order_by(filterby).stream()
            else:
                docs = db.collection(u'user').where(u'is_teacher', u'==', False).order_by(filterby,
                                                                                          direction=firestore.Query.DESCENDING).stream()
        else:
            if sort == "asc":
                docs = db.collection(u'user').where(u'is_teacher', u'==', False).order_by(filterby).limit(20).stream()
            else:
                docs = db.collection(u'user').where(u'is_teacher', u'==', False).order_by(filterby,
                                                                                          direction=firestore.Query.DESCENDING).limit(
                    20).stream()
    elif all:
        docs = db.collection(u'user').where(u'is_teacher', u'==', False).order_by(u'lastname').stream()
    else:
        docs = db.collection(u'user').where(u'is_teacher', u'==', False).order_by(u'lastname').limit(20).stream()
    if docs:
        for doc in docs:
            dict = doc.to_dict()
            dict["id"] = doc.id
            classname = getClassById(dict["class_id"])
            dict["classname"] = classname
            students.append(dict)
        return students
    else:
        return None


# All teachers
def getTeachers(filterby=None, sort=None, all=False):
    teachers = []
    docs = None
    if filterby and sort:
        # search in firstnames, lastnames and id
        if all:
            if sort == "asc":
                docs = db.collection(u'user').where(u'is_teacher', u'==', True).order_by(filterby).stream()
            else:
                docs = db.collection(u'user').where(u'is_teacher', u'==', True).order_by(filterby,
                                                                                         direction=firestore.Query.DESCENDING).stream()
        else:
            if sort == "asc":
                docs = db.collection(u'user').where(u'is_teacher', u'==', True).order_by(filterby).limit(20).stream()
            else:
                docs = db.collection(u'user').where(u'is_teacher', u'==', True).order_by(filterby,
                                                                                         direction=firestore.Query.DESCENDING).limit(
                    20).stream()
    elif all:
        docs = db.collection(u'user').where(u'is_teacher', u'==', True).order_by(u'lastname').stream()
    else:
        docs = db.collection(u'user').where(u'is_teacher', u'==', True).order_by(u'lastname').limit(20).stream()
    if docs:
        for doc in docs:
            dict = doc.to_dict()
            print(dict)
            dict["id"] = doc.id
            teachers.append(dict)
        return teachers
    else:
        return None


### SCHEME FUNCTIONS
# All scheme functions
def addScheme(schedule_week, group_id, room_id):
    groupname = getGroupById(group_id, "groupname")
    roomname = getRoomById(room_id, "roomname")
    data = {
        u'assigned_to': group_id,
        u'room_id': room_id,
        u'schemename': f"{roomname} - {groupname}"
    }

    for key in schedule_week:
        data[key] = schedule_week[key]
    db.collection(u'scheme').add(data)


def deleteScheme(scheme_id):
    # delete the scheme
    db.collection(u'scheme').document(scheme_id).delete()


### GROUP FUNCTIONS
# All ibamaflex classes
def getDefaultGroups():
    classes = []
    docs = None
    docs = db.collection(u'group').stream()
    if docs:
        for doc in docs:
            dict = doc.to_dict()
            if dict["is_class"] is True:
                dict["id"] = doc.id
                if doc.id == "cUJpi7aQjwQ60VHw1sZE":
                    teachers = db.collection(u'user').where(u'is_teacher', u'==', True).stream()
                    if teachers:
                        amount = len(list(teachers))
                        dict["number"] = amount
                    classes.append(dict)
                else:
                    number = db.collection(u'user').where(u'class_id', u'==', doc.id).stream()
                    if number:
                        amount = len(list(number))
                        dict["number"] = amount
                    classes.append(dict)
        return classes
    else:
        return None


# All nonclasses
def getNonDefaultGroups():
    nonclasses = []
    docs = None
    docs = db.collection(u'group').stream()
    if docs:
        for doc in docs:
            dict = doc.to_dict()
            if dict["is_class"] is False:
                # number = db.collection(u'user').where(u'group_id', u'==', doc.id).stream()
                users = db.collection(u'user').stream()
                amount = 0
                if users:
                    for user in users:
                        info = user.to_dict()
                        if info["group_id"]:
                            for group in info["group_id"]:
                                if group == doc.id:
                                    amount += 1

                dict["id"] = doc.id
                dict["number"] = amount
                nonclasses.append(dict)
        return nonclasses
    else:
        return None


def addGroup(groupname):
    data = {
        u'groupname': groupname,
        u'is_class': False,
    }
    db.collection(u'group').add(data)


# All groups
def getAllGroups():
    try:
        return get_firestore_collection("group", order_by="groupname")
    except:
        return None


def getGroupById(group_id, value=None):
    doc_ref = db.collection(u'group').document(group_id)
    doc = doc_ref.get()
    schemes = []
    if doc.exists:
        dict = doc.to_dict()
        if value == "groupname":
            return dict["groupname"]
        else:
            dict["id"] = group_id
            docs_scheme = db.collection(u'scheme').where(u'assigned_to', u'==', group_id).stream()
            if docs_scheme:
                for doc_scheme in docs_scheme:
                    dict_scheme = doc_scheme.to_dict()

                    dict_scheme["id"] = doc_scheme.id
                    schemes.append(dict_scheme)

            return schemes, dict


def getClassById(class_id):
    doc_ref = db.collection(u'group').document(class_id)
    doc = doc_ref.get()
    if doc.exists:
        dict = doc.to_dict()
        groupname = dict["groupname"]
        return groupname


def deleteGroup(group_id):
    # first delete the schemes associated with this room
    doc_scheme = db.collection(u'scheme').where(u'assigned_to', u'==', group_id).get()

    if doc_scheme:
        batch = db.batch()
        for doc in doc_scheme:
            batch.delete(doc.reference)
        batch.commit()

    # delete the group where user is assigned to
    all_users = getUsers()
    for user in all_users:
        print(user["id"])
        user_ref = db.collection(u'user').document(user["id"])

        user_ref.update({u'group_id': firestore.ArrayRemove([group_id])})

    # delete the room itself
    db.collection(u'group').document(group_id).delete()


def deleteUserFromGroup(group_id, user_id):
    user_ref = db.collection(u'user').document(user_id)
    user_ref.update({u'group_id': firestore.ArrayRemove([group_id])})


# GENERAL FUNCTIONS
def getHistoryRoom(room_id, first=None, all=False):
    logs = []
    docs = None
    if first:
        logging_ref = db.collection(u'logging').where(u'room_id', '==', room_id)
        query = logging_ref.order_by(u'datetime', direction=firestore.Query.DESCENDING).limit(1)
        result = query.stream()
        if result:
            for r in result:
                dict_r = r.to_dict()
                dict_r["id"] = r.id
                dict_r["date"] = r.to_dict()['datetime'].date()
                dict_r["time"] = r.to_dict()['datetime'].strftime("%H:%M:%S")
                user = getUserById(dict_r['user_id'])
                if user is None:
                    dict_r["name"] = dict_r['user_id']
                else:
                    dict_r["name"] = user['lastname'] + " " + user['firstname']
                logs.append(dict_r)
        return logs

    else:
        today = datetime.now() - timedelta(days=14)
        query = db.collection(u'logging').where(u'datetime', u'>=', today).order_by(u'datetime',
                                                                                    direction=firestore.Query.DESCENDING)
        if all:
            docs = query.stream()
        else:
            docs = query.limit(20).stream()
        if docs:
            for doc in docs:
                dict = doc.to_dict()
                dict["id"] = doc.id
                dict["date"] = doc.to_dict()['datetime'].date()
                dict["time"] = doc.to_dict()['datetime'].strftime("%H:%M:%S")
                user = getUserById(dict['user_id'])
                if user is None:
                    dict["name"] = dict['user_id']
                else:
                    dict["name"] = user['lastname'] + " " + user['firstname']
                scheme, room_info, _ = getRoomById(dict['room_id'])
                if room_info is None:
                    dict["room"] = "Unknown"
                else:
                    dict["room"] = room_info['roomname']

                logs.append(dict)
            return logs


def getParameters():
    parameters = db.collection(u'general_parameters').document(u'parameters').get()
    if parameters.exists:
        params = parameters.to_dict()
        return params["minimum_accuracy"], params["unlock_seconds"]


def editParameters(req):
    dict_params = {}
    if req['accuracy']:
        accuracy = req['accuracy']
        dict_params['minimum_accuracy'] = int(accuracy)
        dict_params['retrain_model'] = True
    if req['seconds']:
        seconds = req['seconds']
        dict_params['unlock_seconds'] = int(seconds)

    params_ref = db.collection(u'general_parameters').document(u'parameters')
    params_ref.update(dict_params)
