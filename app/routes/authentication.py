from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.auth_forms import LoginForm
from app.models import User

auth_bp = Blueprint('authentication', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip()).first()
        
        if user:
            print(f"User found: {user.username}")
            print(f"Password hash: {user.password_hash}")
        
        if user and user.verify_password(form.password.data.strip()):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            print("Invalid email or password")
            flash('Invalid email or password')
            
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('authentication.login'))