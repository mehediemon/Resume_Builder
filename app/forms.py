from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Email

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class ResumeForm(FlaskForm):
    name = StringField('Name')
    designation = StringField('Designation')
    phone = StringField('Phone')
    email = StringField('Email')
    linkedin = StringField('LinkedIn')
    summary = TextAreaField('Summary')
    experience = TextAreaField('Experience', render_kw={
        "placeholder": 
"""Designation
Company Location
Company Name
Date – Date or Present
Description 1
Description 2
||
Designation
Company Location
Company Name
Date – Date or Present
Description 1
Description 2""",
 "style": "height: 200px;"
    })
    achievements = TextAreaField('Achievements')
    skills = TextAreaField('Skills (comma-separated)')
    education = TextAreaField('Education')
    courses = TextAreaField('Courses / Training')
    submit = SubmitField('Update and View Profile')