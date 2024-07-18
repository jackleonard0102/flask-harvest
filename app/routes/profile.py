from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from app.forms.auth_forms import ProfileForm
from app.extensions import db

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def index():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.name = form.name.data.strip()
        current_user.email = form.email.data.strip()
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('profile.index'))
        
    return render_template('profile.html', form=form)
