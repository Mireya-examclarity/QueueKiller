from flask import Flask, jsonify, request, render_template
from datetime import datetime
from threading import Lock
import os

app = Flask(__name__)

# places where students may have to wait

places = ["Canteen", "Xerox", "Clinic", "Fees Office", "Bus Counter"]
moods = ["Chill", "Normal", "Urgent"]

# each place has its own queue
# next_num stores the next token number

my_queues = {}
for p in places:
    my_queues[p] = {"people": [], "next_num": 1}

lock = Lock()
time_per_person = 2
OWNER_PIN = "1234"

def make_token(n):
    if n < 10:
        return "Q00" + str(n)
    elif n < 100:
        return "Q0" + str(n)
    else:
        return "Q" + str(n)

def get_waiting(list_people):
    waiting = []
    for person in list_people:
        if person["status"] == "waiting":
            waiting.append(person)
    return waiting

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/locations")
def get_locs():
    return jsonify({"locations": places, "moods": moods})

@app.route("/api/queue")
def get_queue():
    loc = request.args.get("location", "Canteen")
    if loc not in places:
        return jsonify({"error": "no such place"}), 400

    with lock:
        people = my_queues[loc]["people"]
        waiting = get_waiting(people)

        serving = None
        for person in people:
            if person["status"] == "serving":
                serving = person
                break

        # calculate the waiting time for each person


        serving_extra = 1 if serving else 0

        for person in people:
            if person["status"] == "waiting":
                ahead = 0
                for other in people:
                    if other["status"] == "waiting" and other["number"] < person["number"]:
                        ahead += 1
                person["wait"] = (ahead + serving_extra) * time_per_person

        if len(waiting) == 0 and serving is None:
            msg = "No one in queue yet. Be first!"
            state = "empty"
        elif len(waiting) == 0 and serving is not None:
            msg = f"Serving {serving['token']} now, no one else waiting"
            state = "serving_only"
        else:
            msg = f"{len(waiting)} waiting"
            state = "waiting"

        tip = ""
        total_wait = (len(waiting) + serving_extra) * time_per_person
        if total_wait > 6:
            tip = "Go grab tea, we'll hold your spot!"

        return jsonify({
            "location": loc,
            "queue": people,
            "waiting_count": len(waiting),
            "serving": serving,
            "next_token": make_token(my_queues[loc]["next_num"]),
            "message": msg,
            "state": state,
            "tip": tip
                                })

@app.route("/api/join", methods=["POST"])
def join():
    data = request.get_json() or {}
    loc = data.get("location", "Canteen")
    mood = data.get("mood", "Normal")
    name = data.get("name", "Student")

    if loc not in places or mood not in moods:
        return jsonify({"error": "invalid"}), 400
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name required"}), 400
    if len(name.strip()) > 30:
        return jsonify({"error": "name too long"}), 400

    with lock:
        q = my_queues[loc]
        num = q["next_num"]
        token = make_token(num)

        # count the person currently being served

        serving_count = 1 if any(p["status"] == "serving" for p in q["people"]) else 0
        wait = (len(get_waiting(q["people"])) + serving_count) * time_per_person

        person = {
            "number": num,
            "token": token,
            "name": name.strip(),
            "location": loc,
            "mood": mood,
            "status": "waiting",
            "created": datetime.now().strftime("%H:%M"),
            "wait": wait}
        
        
        q["people"].append(person)
        q["next_num"] += 1

        return jsonify({
            "token": token,
            "wait": wait,
            "message": f"Your token is {token}"
                                             })

def check_owner(data):
    pin = data.get("pin", "")
    return pin == OWNER_PIN

@app.route("/api/next", methods=["POST"])
def next_person():
    data = request.get_json() or {}
    loc = data.get("location", "Canteen")
    if loc not in places:
        return jsonify({"error": "invalid place"}), 400
    if not check_owner(data):
        return jsonify({"error": "Owner PIN required"}), 403

    with lock:
        people = my_queues[loc]["people"]
        for p in people:
            if p["status"] == "serving":
                p["status"] = "done"
        for p in people:
            if p["status"] == "waiting":
                p["status"] = "serving"
                return jsonify({"now": p["token"], "name": p["name"]})
        return jsonify({"now": None, "message": "no one waiting"})



@app.route("/api/clear", methods=["POST"])
def clear():
    data = request.get_json() or {}
    loc = data.get("location", "Canteen")
    if loc not in places:
        return jsonify({"error": "invalid place"}), 400
    if not check_owner(data):
        return jsonify({"error": "Owner PIN required"}), 403
    with lock:
        my_queues[loc]["people"] = []
        my_queues[loc]["next_num"] = 1
    return jsonify({"message": "Queue cleared"})


@app.route("/api/demo", methods=["POST"])
def demo():
    data = request.get_json() or {}
    loc = data.get("location", "Canteen")
    if loc not in places:
        return jsonify({"error": "invalid place"}), 400
    if not check_owner(data):
        return jsonify({"error": "Owner PIN required"}), 403


    with lock:
        q = my_queues[loc]
        for p in q["people"]:
            if p.get("demo"):
                return jsonify({"message": "Demo already there"})
        for i in range(3):
            num = q["next_num"]
            serving_extra = 1 if any(x["status"] == "serving" for x in q["people"]) else 0
            wait = (len(get_waiting(q["people"])) + serving_extra) * time_per_person
            q["people"].append({
                "number": num,
                "token": make_token(num),
                "name": f"Demo {i+1}",
                "location": loc,
                "mood": moods[i],
                "status": "waiting",
                "created": datetime.now().strftime("%H:%M"),
                "wait": wait,
                "demo": True
            })


            q["next_num"] += 1
    return jsonify({"message": "Demo added"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))