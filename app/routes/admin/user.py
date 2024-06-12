from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Customer
from app.extensions import db, bcrypt

# Change the blueprint name to 'admin_user_bp'
admin_user_bp = Blueprint('admin_user_bp', __name__)

@admin_user_bp.route('/admin/user')
@login_required
def index():
    if current_user.permission != 0:  #superadmin role for user management
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    children_1 = User.query.filter(User.permission > 0).all()
    children_2 = Customer.query.filter(Customer.deleted_at == None, Customer.status == 'active').all()
    
    # Create a dictionary to map company_id to company.name
    company_map = {customer.id: customer.name for customer in children_2}
    
    return render_template('admin/user.html', current_user=current_user, children_1=children_1, children_2=children_2, company_map=company_map)

@admin_user_bp.route('/add_user_modal', methods=['POST'])
@login_required
def add_user_modal():
    if current_user.permission not in [0, 1]:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    username = request.form['username']
    email = request.form['email']
    company_id = request.form['company_id']
    permission = request.form['permission']
    password = request.form['password']

    if not username or not email or not company_id or not permission or not password:
        flash('All fields are required.')
        return redirect(url_for('admin_user_bp.index'))

    # Generate password hash using bcrypt
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    new_user = User(
        username=username,
        email=email,
        company_id=company_id,
        permission=permission,
        password_hash=password_hash
    )
    db.session.add(new_user)
    db.session.commit()
    flash('User successfully added!')
    return redirect(url_for('admin_user_bp.index'))

@admin_user_bp.route('/edit_user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.permission not in [0, 1]:  # Only superadmin or admin can edit users
        flash('Unauthorized access')
        return redirect(url_for('admin_user_bp.index'))

    username = request.form['username']
    email = request.form['email']
    company_id = request.form['company_id']
    permission = request.form['permission']

    if not username or not email or not company_id or not permission:
        flash('All fields except password are required.')
        return redirect(url_for('admin_user_bp.index'))

    user.username = username
    user.email = email
    user.company_id = company_id
    user.permission = permission

    db.session.commit()
    flash('User successfully updated!')
    return redirect(url_for('admin_user_bp.index'))

@admin_user_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.permission not in [0, 1]:  # Only superadmin or admin can delete users
        flash('Unauthorized access')
        return redirect(url_for('admin_user_bp.index'))  # Update the URL endpoint to 'admin_user_bp.index'

    db.session.delete(user)
    db.session.commit()
    flash('User successfully deleted!')
    return redirect(url_for('admin_user_bp.index'))  # Update the URL endpoint to 'admin_user_bp.index'