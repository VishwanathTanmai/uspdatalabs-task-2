from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth
from .. import db
from ..models import User

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            # flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('auth/login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print("DEBUG: Signup POST received")
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"DEBUG: Form data - Name: {name}, Username: {username}, Password: {'*' * len(password) if password else 'None'}")
        
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"DEBUG: Username {username} already exists")
            flash('Username already exists.', 'error')
            return redirect(url_for('auth.signup'))
        
        try:
            new_user = User(
                name=name,
                username=username,
                password=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            print("DEBUG: User committed to DB")
            
            login_user(new_user)
            print("DEBUG: User logged in")
            # flash('Account created!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            print(f"DEBUG: Error during signup: {e}")
            flash(f"Error signing up: {str(e)}", 'error')
            return render_template('auth/signup.html')
            
    return render_template('auth/signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
