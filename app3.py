from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import random

app = Flask(__name__)

queue = []
counter = 1
served = 0


# =========================================================
# HOME
# =========================================================

@app.route('/')
def home():
    waiting = [q for q in queue if q['status'] == 'waiting']

    return render_template(
        'index.html',
        queue=queue,
        waiting=waiting,
        served=served,
        counter=counter
    )


# =========================================================
# ADD PERSON TO QUEUE
# =========================================================

@app.route('/add', methods=['POST'])
def add():
    global counter

    name = request.form.get('name')
    place = request.form.get('place')
    vibe = request.form.get('vibe')

    if not name:
        return redirect('/')

    token = f"Q{counter:03d}"

    entry = {
        "token": token,
        "name": name,
        "place": place,
        "vibe": vibe,

        "color": random.choice([
            "#FF6B6B",
            "#4D96FF",
            "#6BCB77"
        ]),

        "time": datetime.now().strftime("%I:%M %p"),

        # New queue system
        "status": "waiting"
    }

    queue.append(entry)
    counter += 1

    # Send the user directly to their personal queue page
    return redirect(url_for('personal_queue', token=token))


# =========================================================
# NEXT CUSTOMER
# =========================================================

@app.route('/next')
def next_token():
    global served

    # Finish the person currently being served
    for person in queue:
        if person['status'] == 'serving':
            person['status'] = 'done'
            served += 1
            break

    # Start serving the next waiting person
    for person in queue:
        if person['status'] == 'waiting':
            person['status'] = 'serving'
            break

    return redirect('/')


# =========================================================
# FIND POSITION IN QUEUE
# =========================================================

def get_position(token):

    active_queue = [
        person for person in queue
        if person['status'] in ['waiting', 'serving']
    ]

    for index, person in enumerate(active_queue):

        if person['token'] == token:
            return index

    return None


# =========================================================
# PERSONAL QUEUE PAGE
# =========================================================

@app.route('/queue/<token>')
def personal_queue(token):

    person = next(
        (p for p in queue if p['token'] == token),
        None
    )

    if not person:
        return "Token not found", 404

    position = get_position(token)

    if position is not None:

        # Serving person has position 0
        people_ahead = max(position - 1, 0)

        # Temporary estimate:
        # 2 minutes per person
        wait_time = people_ahead * 2

    else:

        people_ahead = 0
        wait_time = 0

    return render_template(
        'queue.html',

        person=person,

        people_ahead=people_ahead,

        wait_time=wait_time
    )


# =========================================================
# LIVE QUEUE API
# =========================================================

@app.route('/api/queue/<token>')
def queue_status(token):

    person = next(
        (p for p in queue if p['token'] == token),
        None
    )

    if not person:
        return jsonify({
            "error": "Token not found"
        }), 404

    position = get_position(token)

    if position is not None:

        people_ahead = max(position - 1, 0)

    else:

        people_ahead = 0

    wait_time = people_ahead * 2

    return jsonify({

        "token": token,

        "name": person["name"],

        "status": person["status"],

        "people_ahead": people_ahead,

        "wait_time": wait_time

    })


# =========================================================
# LEAVE QUEUE
# =========================================================

@app.route('/leave/<token>')
def leave_queue(token):

    for person in queue:

        if person['token'] == token:

            if person['status'] == 'waiting':
                person['status'] = 'cancelled'

            break

    return redirect('/')


# =========================================================
# GENERAL QUEUE API
# =========================================================

@app.route('/api/queue')
def queue_api():

    current = next(
        (
            person['token']
            for person in queue
            if person['status'] == 'serving'
        ),
        None
    )

    waiting_count = len([
        person for person in queue
        if person['status'] == 'waiting'
    ])

    active_count = len([
        person for person in queue
        if person['status'] in ['waiting', 'serving']
    ])

    return jsonify({

        "current": current,

        "waiting": waiting_count,

        "total_active": active_count

    })


# =========================================================
# CLEAR QUEUE
# =========================================================

@app.route('/clear')
def clear():

    global queue, counter

    queue = []

    counter = 1

    return redirect('/')


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )


