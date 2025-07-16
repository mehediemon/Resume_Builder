from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    profile = db.relationship('Resume', backref='owner', uselist=False)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    designation = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    linkedin = db.Column(db.String(200))
    summary = db.Column(db.Text)
    experience = db.Column(db.Text)
    achievements = db.Column(db.Text)
    skills = db.Column(db.Text)
    education = db.Column(db.Text)
    courses = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class ResumeHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resume_snapshot = db.Column(db.Text)  # JSON string or pickled object
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'))
    resume = db.relationship('Resume', backref='history')