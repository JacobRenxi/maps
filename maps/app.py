from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import os
from models import db, User, Marker  # Assuming you have imported the necessary modules
import bcrypt

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db.init_app(app)

# Initialize SocketIO
socketio = SocketIO(app)

# Routes

@app.route('/')
def index():
    if 'username' in session:
        markers = Marker.query.all()
        return render_template('map.html', markers=markers)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already taken')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username
        return redirect(url_for('index'))

    return render_template('register.html')

# WebSocket event handlers

@socketio.on('add_marker')
def handle_add_marker(data):
    lat, lng, name, event, time = data['lat'], data['lng'], data['name'], data['event'], data['time']
    new_marker = Marker(lat=lat, lng=lng, name=name, event=event, time=time)
    db.session.add(new_marker)
    db.session.commit()
    emit('new_marker', {'lat': lat, 'lng': lng, 'name': name, 'event': event, 'time': time}, broadcast=True)

@socketio.on('delete_marker')
def handle_delete_marker(data):
    lat, lng = data['lat'], data['lng']
    marker = Marker.query.filter_by(lat=lat, lng=lng).first()
    if marker:
        db.session.delete(marker)
        db.session.commit()
        emit('marker_deleted', {'lat': lat, 'lng': lng}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables within the application context

    socketio.run(app, debug=True)
