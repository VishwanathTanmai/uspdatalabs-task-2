from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) # Added name field
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    uploads = db.relationship('ImageUpload', backref='author', lazy=True)

class ImageUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filepath = db.Column(db.String(500), nullable=False)
    processed_filepath = db.Column(db.String(500))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # made nullable for demo without login
    results = db.Column(db.Text) # JSON string of results
    tags = db.Column(db.String(500)) # Comma separated list of detected objects
