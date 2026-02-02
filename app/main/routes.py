from flask import render_template
from flask_login import login_required, current_user
from . import main

@main.route('/')
def index():
    return render_template('landing.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
