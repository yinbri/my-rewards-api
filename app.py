from flask import Flask, jsonify, request
import json
from pymongo import MongoClient

URI = "mongodb://localhost:27017"

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/login_service', methods=['POST'])
def login():
    myclient = MongoClient(URI)
    mydb = myclient["mydb"]
    mycol = mydb["user"]

    content = request.get_json()
    print(content)
    username = content.get("username")
    password = content.get("password")
    print('receive: ', username, ' ', password)
    result = mycol.find({"$and": [{"username": username}, {"password": password}]})

    mylist = list(result)

    have_list = True if len(mylist) else False;

    if have_list:
        user = mylist[0]
        myclient.close()
        return {"status": "success", "username": username}
    else:
        print("Not found ", username)
        myclient.close()
        return {"status": "failed",
                "message": "Username does not exist. Please enroll first."}


@app.route('/enrollment_service', methods=['POST'])
def enroll():
    content = request.get_json()
    print(content)
    username = content.get("username")
    password = content.get("password")
    print('receive: ', username, ' ', password)

    myclient = MongoClient(URI)
    mydb = myclient["mydb"]
    mycol = mydb["user"]

    existing = False
    result = mycol.find({"username": username})
    mylist = list(result)

    existing = False
    data = {}
    for item in mylist:
        if username == item['email']:
            existing = True
            print("found ", username)
            return {"status": "failed", "message": "user exists already"}
    if not existing:
        mycol.insert_one({"username": username, "password": password})
        return {"status": "success"}

# mark to be deleted
@app.route('/activities_service', methods=['GET'])
def get_all_activities():
    myclient = MongoClient(URI)
    mydb = myclient["mydb"]
    mycol = mydb["activity"]
    mylist = list(mycol.find({}, {"_id": 0, "id": 1, "date": 1, "place":1, "description": 1, "points": 1, "enrolled": "No"}))
    print(mylist)
    myclient.close()
    return {"status": "success", "activitylist": mylist}

# used by: user flow
# this function returns all activities that a student user can see
# it also indicator whether an activity had been enrolled or attended
@app.route('/eligible_activity_service', methods=['POST'])
def get_eligible_activities_for_one_student():
    req = request.get_json()
    username = req.get("username")

    myclient = MongoClient(URI)
    mydb = myclient["mydb"]

    mycol = mydb["activity"]
    all_activities = list(mycol.find({}, {"_id": 0, "id": 1, "date": 1, "place":1, "description": 1, "points": 1, "status": "Unenrolled"}))

    mycol2 = mydb["useractivity"]
    user_activities = list(mycol2.find({"username": username}))

    id_status_dict = {}
    for i in range(0, len(user_activities)):
        id_status_dict.update({user_activities[i]["id"]: user_activities[i]["status"]})

    value = []
    for j in range(0, len(all_activities)):
        item = all_activities[j]
        status = id_status_dict.get(item["id"])
        if status is None:
            item["status"] = "Unenrolled"
            value.append(item)
        elif status == "Enrolled":
            item["status"] = status
            value.append(item)

    return {"status": "success", "activities": value}

def login2():
    username = request.form['username']
    password = request.form['password']
    print('receive: ', username, ' ', password)
    for item in data['user_list']:
        if username == item['user_name'] and password == item['password']:
            return 'success', 200
    return 'failed', 204

# mark to be deleted
@app.route('/optin_service', methods=['POST'])
def optIn():
    req = request.get_json()
    username = req.get("username")

    myclient = MongoClient(URI)
    mydb = myclient["mydb"]
    mycol = mydb["user"]
    result = mycol.find({"email": req["username"]})
    mylist = list(result)
    have_list = True if len(mylist) else False;

    if have_list:
        user = mylist[0]
        my_activities = user["activities"]
        if not (req["activity"] in my_activities):
            my_activities.append(req["activity"])
            mycol.update_one({"email": username}, {"$set": {"activities": my_activities}})
            myclient.close()
            return {"status": "success"}
        else:
            return {"status": "success", "message": "opt-in already"}
    else:
        return {"status": "error", "message": "user can't be found"}


# used by: user flow
# this API returns the enrolled or attended activities for a student
# if also return total pending and total earned points
@app.route('/rewards_activity_service', methods=['POST'])
def getUsersRewards():
    req = request.get_json()
    username = req["username"]

    myclient = MongoClient(URI)
    mydb = myclient["mydb"]
    mycol = mydb["useractivity"]

    result = mycol.find({"username": username},{"_id":0,"username":1, "id":1, "date":1, "place":1, "description":1, "points":1, "status":1})
    mylist = list(result)

    total_earned = 0
    total_pending = 0
    for item in mylist:
        if item["status"] == "Enrolled":
            total_pending += item["points"]
        elif item["status"] == "Attended":
            total_earned += item["points"]

    return {"status": "success", "total_earned": total_earned, "total_pending": total_pending, "useractivities": mylist}

# used by: user flow & admin flow
# it updates the status of an activity for a student
@app.route('/update_enrollment_service', methods=['POST'])
def updateEnrollment():
    print("update enrollment service: start")
    req = request.get_json()
    print("request =", req)

    username = req.get("username")
    row_data = req.get("rowvalue")
    event_id = row_data["id"]
    date = row_data["date"]
    place = row_data["place"]
    description = row_data["description"]
    points = row_data["points"]
    status = row_data["status"]

    # find an existing user activity if there is one.
    myclient = MongoClient(URI)
    mydb = myclient["mydb"]
    mycol = mydb["useractivity"]

    ret_value = {}

    if status == "Enrolled":
        print("insert.....")
        mycol.insert_one({"username": username,"id": event_id, "date": date,"place": place,"description": description,"points": points, "status": "Enrolled"})
        ret_value = {"status": "success", "message":"Enrolled"}
    elif status == "Attended":
        print("update.....")
        mycol.update_one({"username": username, "id": event_id}, {"$set": {"status": "Attended"}})
        ret_value = {"status": "success", "message": "Status updated to Attended"}
    elif status == "Unenrolled":
        print("delete.....")
        mycol.delete_one({"username": username, "id": event_id})
        ret_value = {"status": "success", "message": "Unenrolled"}

    myclient.close()
    return ret_value

# used by: admin flow
# it validate the user provided username and password against the record in database
@app.route('/admin_login_service', methods=['POST'])
def admin_user_login():
    req = request.get_json()
    username = req.get("username")
    password = req.get("password")
    myclient = MongoClient(URI)
    mydb = myclient["mydb"]
    mycol = mydb["adminuser"]
    result = mycol.find({"username": username, "password": password})
    mylist = list(result)
    have_list = True if len(mylist) else False;

    if have_list:
        return {"status": "success"}
    else:
        return {"status": "failed"}

# used by: admin flow
# it returns all users' activities
@app.route('/pending_user_activities_service', methods=['POST'])
def get_all_user_activities():
    myclient = MongoClient(URI)
    mydb = myclient["mydb"]
    mycol = mydb["useractivity"]
    result = mycol.find({}, {"_id": 0,"username":1, "id":1, "date":1, "place":1, "description":1, "points":1, "status":1})
    mylist = list(result)
    have_list = True if len(mylist) else False;

    if have_list:
        return {"status": "success", "useractivities": mylist}
    else:
        return {"status": "failed"}

@app.route('/leader_board_service', methods=['GET'])
def leader_board_activities():
    myclient = MongoClient(URI)
    mydb = myclient["mydb"]
    mycol = mydb["useractivity"]
    result = mycol.aggregate( [{"$group": {"_id": {"username": "$username"}, "Total": {"$sum": "$points"}}}, {"$sort": {"Total":-1}}])
    mylist = list(result)

    print(mylist)

    have_list = True if len(mylist) else False;

    value = []
    if have_list:
        for i in range(0, len(mylist)):
            username = getName(mylist[i]["_id"]["username"])
            total = mylist[i]["Total"]
            value.append({"username": username, "total": total})
        return {"status": "success", "leaders": value}
    else:
        return {"status": "failed"}


def getName(email_address):
    r = email_address.index("@")
    return "".join(l for l in email_address[:r])


'''
db.useractivity.aggregate( {$group: {"_id": {"username": "$username", "status": "$status"}, "Total": { $sum: "$points"}}})
db.useractivity.aggregate( {$group: {"username":"brianyin27@gmail.com", "Total": { $sum: "$points"}} })

'''