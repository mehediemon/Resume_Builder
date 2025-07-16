from app import app, db
from flask import render_template, redirect, url_for, request, send_file, abort
from app.models import User, Resume, ResumeHistory
from app.forms import RegisterForm, LoginForm, ResumeForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager
from weasyprint import HTML
import io
import json
from datetime import datetime, timedelta
from collections import defaultdict

def serialize_resume(resume):
    return json.dumps({
        "name": resume.name,
        "designation": resume.designation,
        "phone": resume.phone,
        "email": resume.email,
        "linkedin": resume.linkedin,
        "summary": resume.summary,
        "experience": resume.experience,
        "achievements": resume.achievements,
        "skills": resume.skills,
        "education": resume.education,
        "courses": resume.courses
    })

def deserialize_resume(json_string):
    try:
        return json.loads(json_string)
    except Exception:
        return {}

def extract_skills(skills_text):
    """Helper to get list of skills from the text field (assuming comma or newline separated)."""
    if not skills_text:
        return []
    # Split by comma or newline and strip whitespace
    skills = [s.strip() for s in skills_text.replace('\n', ',').split(',') if s.strip()]
    return skills

def get_new_items(old_list, new_list):
    """Return items that are in new_list but not in old_list."""
    return list(set(new_list) - set(old_list))

def check_field_changes_with_names(history_list, since):
    """Checks changes and collects new skill names, achievements, and courses added after 'since'."""
    filtered = [h for h in history_list if h.timestamp >= since]
    filtered.sort(key=lambda h: h.timestamp)  # Sort ascending
    
    new_skills_flag = False
    new_achievements_flag = False
    new_courses_flag = False
    
    new_skills_names = []
    new_achievements_texts = []
    new_courses_texts = []
    
    prev = None
    for h in filtered:
        current = deserialize_resume(h.resume_snapshot)
        if prev:
            # Check skills difference
            prev_skills = extract_skills(prev.get("skills"))
            curr_skills = extract_skills(current.get("skills"))
            new_skills = get_new_items(prev_skills, curr_skills)
            if new_skills:
                new_skills_flag = True
                new_skills_names.extend(new_skills)
            
            # Check achievements difference (simple text comparison)
            if current.get("achievements") != prev.get("achievements"):
                new_achievements_flag = True
                new_achievements_texts.append(current.get("achievements"))
            
            # Check courses difference
            if current.get("courses") != prev.get("courses"):
                new_courses_flag = True
                new_courses_texts.append(current.get("courses"))
                
        prev = current
    
    # Remove duplicates
    new_skills_names = list(set(new_skills_names))
    new_achievements_texts = list(set(new_achievements_texts))
    new_courses_texts = list(set(new_courses_texts))
    
    return {
        "skills_flag": new_skills_flag,
        "achievements_flag": new_achievements_flag,
        "courses_flag": new_courses_flag,
        "skills_names": new_skills_names,
        "achievements_texts": new_achievements_texts,
        "courses_texts": new_courses_texts,
    }


@app.route('/')
def home():
    return render_template('landing.html')

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
            return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    resume = current_user.profile
    form = ResumeForm(obj=resume)

    if form.validate_on_submit():
        is_update = resume is not None
        if is_update:
            # Save snapshot before updating
            history = ResumeHistory(
                resume_snapshot=serialize_resume(resume),
                resume=resume
            )
            db.session.add(history)
            form.populate_obj(resume)
        else:
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
        return redirect(url_for('view_profile'))

    return render_template('profile.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    resume = current_user.profile
    if not resume:
        return redirect(url_for('profile'))

    now = datetime.utcnow()
    one_month_ago = now - timedelta(days=30)
    three_months_ago = now - timedelta(days=90)

    history = ResumeHistory.query.filter_by(resume=resume).all()

    def count_updates(since):
        return sum(1 for h in history if h.timestamp >= since)

    updates_last_month = count_updates(one_month_ago)
    updates_last_3_months = count_updates(three_months_ago)

    changes_1m = check_field_changes_with_names(history, one_month_ago)
    changes_3m = check_field_changes_with_names(history, three_months_ago)


    return render_template('dashboard.html',
                           updates_last_month=updates_last_month,
                           updates_last_3_months=updates_last_3_months,
                           changes_1m=changes_1m,
                           changes_3m=changes_3m
                           )

@app.route('/view-profile')
@login_required
def view_profile():
    resume = current_user.profile
    if not resume:
        return redirect(url_for('profile'))
    return render_template('resume_saved.html', resume=resume, resume_id=resume.id)

@app.route('/resume/<int:resume_id>/success')
@login_required
def resume_success(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.owner != current_user:
        abort(403)
    return render_template('resume_saved.html', resume=resume, resume_id=resume.id)

@app.route('/resume/<int:resume_id>/pdf')
@login_required
def generate_pdf(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.owner != current_user:
        abort(403)

    rendered = render_template("resume_template.html", resume=resume)
    pdf = HTML(string=rendered).write_pdf()

    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        download_name='resume.pdf',
        as_attachment=True
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('landing.html')
