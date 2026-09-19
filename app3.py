from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import random

app = Flask(__name__)

queue = []
counter = 1
served = 0

@app.route('/')
def home():
    waiting = [q for q in queue if q['status'] == 'waiting']
    return render_template('index.html', queue=queue, waiting=waiting, served=served, counter=counter)

@app.route('/add', methods=['POST'])
def add():
    global counter
    name = request.form.get('name')
    place = request.form.get('place')
    vibe = request.form.get('vibe')
    if not name: return redirect('/')
    token = f"Q{counter:03d}"
    entry = {
        "token": token, "name": name, "place": place,
        "vibe": vibe, "color": random.choice(["#FF6B6B","#4D96FF","#6BCB77"]),
        "time": datetime.now().strftime("%I:%M %p"), "status": "waiting"
    }
    queue.append(entry)
    counter += 1
    return redirect('/')

@app.route('/next')
def next_token():
    global served
    for p in queue:
        if p['status'] == 'waiting':
            p['status'] = 'done'
            served += 1
            break
    return redirect('/')

@app.route('/clear')
def clear():
    global queue, counter
    queue = []
    counter = 1
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)