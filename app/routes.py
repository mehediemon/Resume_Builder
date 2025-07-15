from app import app, db, routes
from flask import render_template, redirect, url_for, request, send_file
from app.models import User, Resume
from app.forms import RegisterForm, LoginForm, ResumeForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager
from weasyprint import HTML
import io

@app.route('/')
def home():
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = ResumeForm()
    if form.validate_on_submit():
        resume = Resume(
            name=form.name.data,
            designation=form.designation.data,
            phone=form.phone.data,
            email=form.email.data,
            linkedin=form.linkedin.data,
            summary=form.summary.data,
            experience=form.experience.data,
            achievements=form.achievements.data,
            skills=form.skills.data,
            education=form.education.data,
            courses=form.courses.data,
            owner=current_user
        )
        db.session.add(resume)
        db.session.commit()

        rendered = render_template("resume_template.html", resume=resume)
        pdf = HTML(string=rendered).write_pdf()
        return send_file(
                io.BytesIO(pdf),
                mimetype='application/pdf',
                download_name='resume.pdf',
                as_attachment=False  # important to prevent download
                )
    return render_template('dashboard.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))