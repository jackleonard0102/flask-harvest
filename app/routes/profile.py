from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from app.forms.auth_forms import ProfileForm
from app.extensions import db
from werkzeug.security import check_password_hash, generate_password_hash

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def index():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check current password
        if not current_user.verify_password(form.current_password.data):
            flash('Current password is incorrect.')
            return redirect(url_for('profile.index'))

        # Update name and email
        current_user.username = form.username.data.strip()
        current_user.email = form.email.data.strip()

        # Update password if new password is provided
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
        
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('profile.index'))
        
    return render_template('profile.html', form=form)
