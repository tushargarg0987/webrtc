from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    # Add your own authentication logic here
    if username == 'user' and password == 'pass':
        token = jwt.encode({'username': username}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('store_user')
def handle_store_user(data):
    username = data['name']
    users[username] = request.sid
    join_room(request.sid)
    print(f"User {username} stored with SID {request.sid}")

@socketio.on('connect')
def connect():
    print('Client connected', request.sid)

@socketio.on('disconnect')
def disconnect():
    for name, sid in users.items():
        if sid == request.sid:
            del users[name]
            print(f"User {name} deleted")
            break
    print('Client disconnected', request.sid)

@socketio.on('start_call')
def handle_start_call(data):
    target = data['target']
    caller = data['name']
    if target in users:
        print('call_started', {'caller': caller}, "target", users[target])
        emit('call_started', {'caller': caller}, room=users[target])
    else:
        print(f"Target {target} not found in users")

@socketio.on('create_offer')
def handle_create_offer(data):
    target = data['target']
    sdp = data['sdp']
    if target in users:
        print('offer_received', {'sdp': sdp, 'name': data['name']}, "target", users[target])
        emit('offer_received', {'sdp': sdp, 'name': data['name']}, room=users[target])
    else:
        print(f"Target {target} not found in users")

@socketio.on('create_answer')
def handle_create_answer(data):
    target = data['target']
    sdp = data['sdp']
    print("create_answer", data, users)
    if target in users:
        print('answer_received', {'sdp': sdp, 'name': data['name']}, "target:", users[target])
        emit('answer_received', {'sdp': sdp, 'name': data['name']}, room=users[target])
    else:
        print(f"Target {target} not found in users during create")

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    target = data['target']
    candidate = data['candidate']
    if target in users:
        print('ice_candidate', {'candidate': candidate, 'name': data['name']}, "target",users[target])
        emit('ice_candidate', {'candidate': candidate, 'name': data['name']}, room=users[target])
    else:
        print(f"Target {target} not found in users")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)
