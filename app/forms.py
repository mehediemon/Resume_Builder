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
    experience = TextAreaField('Experience')
    achievements = TextAreaField('Achievements')
    skills = TextAreaField('Skills (comma-separated)')
    education = TextAreaField('Education')
    courses = TextAreaField('Courses / Training')
    submit = SubmitField('Save and Download PDF')