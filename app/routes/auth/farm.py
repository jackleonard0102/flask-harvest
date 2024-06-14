from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Farm, Customer
from app.extensions import db, bcrypt


auth_farm_bp = Blueprint('auth_farm_bp', __name__)

@auth_farm_bp.route('/auth/farm')
@login_required
def index():
    if current_user.permission !=1 :  # Assuming 0 and 1 are permissions for superauth and auth
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    children_1 = Farm.query.filter(Farm.company_id == current_user.company_id, Farm.deleted_at == None).all()
    children_2 = Customer.query.filter(Customer.id == current_user.company_id, Customer.deleted_at == None)
    # Create a dictionary to map company_id to company.name
    company_map = {customer.id: customer.name for customer in children_2}
    
    return render_template('auth/farm.html', current_user=current_user, children_1=children_1, children_2=children_2, company_map=company_map)

@auth_farm_bp.route('/auth/add_farm_modal', methods=['POST'])
@login_required
def add_farm_modal():
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    name = request.form['name']
    email = request.form['email']
    company_id = request.form['company_id']
    address = request.form['address']

    if not name or not email or not company_id or not address:
        flash('All fields are required.')
        return redirect(url_for('auth_farm_bp.index'))

    new_farm = Farm(
        name=name,
        email=email,
        company_id=company_id,
        address=address,
    )
    db.session.add(new_farm)
    db.session.commit()
    flash('Farm successfully added!')
    return redirect(url_for('auth_farm_bp.index'))


@auth_farm_bp.route('/auth/edit_farm/<int:farm_id>', methods=['POST'])
@login_required
def edit_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if current_user.permission != 1:  # Only superauth or auth can edit farms
        flash('Unauthorized access')
        return redirect(url_for('auth_farm_bp.index'))

    name = request.form['name']
    email = request.form['email']
    company_id = request.form['company_id']
    address = request.form['address']

    if not name or not email or not company_id or not address:
        flash('All fields except password are required.')
        return redirect(url_for('auth_farm_bp.index'))

    farm.name = name
    farm.email = email
    farm.company_id = company_id
    farm.address = address

    db.session.commit()
    flash('Farm successfully updated!')
    return redirect(url_for('auth_farm_bp.index'))

@auth_farm_bp.route('/auth/delete_farm/<int:farm_id>')
@login_required
def delete_farm(farm_id):
    farm = Farm.query.get_or_404(farm_id)
    if current_user.permission != 1:  # Only superauth or auth can delete farms
        flash('Unauthorized access')
        return redirect(url_for('auth_farm_bp.index'))  # Update the URL endpoint to 'auth_farm_bp.index'

    db.session.delete(farm)
    db.session.commit()
    flash('farm successfully deleted!')
    return redirect(url_for('auth_farm_bp.index'))  # Update the URL endpoint to 'auth_farm_bp.index'