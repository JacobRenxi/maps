from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Marker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Marker {self.name} - Lat: {self.lat}, Lng: {self.lng}>'
