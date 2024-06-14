from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Customer
from app.extensions import db, bcrypt

# Change the blueprint name to 'auth_user_bp'
auth_user_bp = Blueprint('auth_user_bp', __name__)

# auth user table
@auth_user_bp.route('/auth/user')
@login_required
def index():
    if current_user.permission != 1:  # Assuming 0 and 1 are permissions for superadmin and admin
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    children_1 = User.query.filter(User.permission > 1, current_user.company_id == User.company_id).all()
    children_2 = Customer.query.filter(Customer.id == current_user.company_id, Customer.deleted_at == None)
    
    # Create a dictionary to map company_id to company.name
    company_map = {customer.id: customer.name for customer in children_2}
    
    return render_template('auth/user.html', current_user=current_user, children_1=children_1, children_2=children_2, company_map=company_map)


# auth add user
@auth_user_bp.route('/auth/add_user_modal', methods=['POST'])
@login_required
def add_user_modal():
    # Check if the current user has permission to add a new user
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    # Retrieve form data
    username = request.form.get('username')
    email = request.form.get('email')
    company_id = request.form.get('company_id')
    permission = request.form.get('permission')
    password = request.form.get('password')

    # Validate form data
    if not all([username, email, permission, password]):
        flash('All fields are required.')
        return redirect(url_for('auth_user_bp.index'))

    # Check if the email is unique
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email is already in use.')
        return redirect(url_for('auth_user_bp.index'))

    # Generate password hash using bcrypt
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Create a new user object
    new_user = User(
        username=username,
        email=email,
        company_id=company_id,
        permission=permission,
        password_hash=password_hash
    )

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    flash('User successfully added!')
    return redirect(url_for('auth_user_bp.index'))


# auth edit user
@auth_user_bp.route('/auth/edit_user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.permission != 1:  
        flash('Unauthorized access')
        return redirect(url_for('auth_user_bp.index'))

    username = request.form['username']
    email = request.form['email']
    company_id = request.form['company_id']
    permission = request.form['permission']

    if not username or not email or not company_id or not permission:
        flash('All fields except password are required.')
        return redirect(url_for('auth_user_bp.index'))

    user.username = username
    user.email = email
    user.company_id = company_id
    user.permission = permission

    db.session.commit()
    flash('User successfully updated!')
    return redirect(url_for('auth_user_bp.index'))

@auth_user_bp.route('/auth/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.permission != 1:  
        flash('Unauthorized access')
        return redirect(url_for('auth_user_bp.index'))  # Update the URL endpoint to 'auth_user_bp.index'

    db.session.delete(user)
    db.session.commit()
    flash('User successfully deleted!')
    return redirect(url_for('auth_user_bp.index'))  # Update the URL endpoint to 'auth_user_bp.index'