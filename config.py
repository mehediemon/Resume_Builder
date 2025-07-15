import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://resumeuser:yourpassword@localhost:5432/resume_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
