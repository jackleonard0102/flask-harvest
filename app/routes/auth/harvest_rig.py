from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import HarvestRig, Customer  # Import your models accordingly
from app.extensions import db

auth_harvest_rig_bp = Blueprint('auth_harvest_rig_bp', __name__)

@auth_harvest_rig_bp.route('/auth/harvest_rig')
@login_required
def index():
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    children_1 = HarvestRig.query.all()
    children_2 = Customer.query.filter(Customer.deleted_at.is_(None), Customer.status == 'active').all()
    
    # Create a dictionary to map company_id to company.name
    company_map = {customer.id: customer.name for customer in children_2}
    
    return render_template('auth/harvest_rig.html', current_user=current_user, children_1=children_1, children_2=children_2, company_map=company_map)

@auth_harvest_rig_bp.route('/auth/add_harvest_rig_modal', methods=['POST'])
@login_required
def add_harvest_rig_modal():
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    company_id = request.form['company_id']
    name = request.form['name']
    year = request.form['year']
    serial_number = request.form['serial_number']
    operator = request.form['operator']

    if not name or not year or not serial_number or not operator:
        flash('All fields are required.')
        return redirect(url_for('auth_harvest_rig_bp.index'))

    new_harvest_rig = HarvestRig(
        name=name,
        year=year,
        serial_number=serial_number,
        current_operator_id=operator,
        company_id=company_id
    )
    db.session.add(new_harvest_rig)
    db.session.commit()
    flash('HarvestRig successfully added!')
    return redirect(url_for('auth_harvest_rig_bp.index'))

@auth_harvest_rig_bp.route('/auth/edit_harvest_rig/<int:harvest_rig_id>', methods=['POST'])
@login_required
def edit_harvest_rig(harvest_rig_id):
    harvest_rig = HarvestRig.query.get_or_404(harvest_rig_id)
    if current_user.permission != 1:  
        flash('Unauthorized access')
        return redirect(url_for('auth_harvest_rig_bp.index'))

    name = request.form['name']
    year = request.form['year']
    serial_number = request.form['serial_number']
    operator = request.form['operator']

    if not name or not year or not serial_number or not operator:
        flash('All fields are required.')
        return redirect(url_for('auth_harvest_rig_bp.index'))

    harvest_rig.name = name
    harvest_rig.year = year
    harvest_rig.serial_number = serial_number
    harvest_rig.current_operator_id = operator

    db.session.commit()
    flash('HarvestRig successfully updated!')
    return redirect(url_for('auth_harvest_rig_bp.index'))

@auth_harvest_rig_bp.route('/auth/delete_harvest_rig/<int:harvest_rig_id>')
@login_required
def delete_harvest_rig(harvest_rig_id):
    harvest_rig = HarvestRig.query.get_or_404(harvest_rig_id)
    if current_user.permission != 1:  
        flash('Unauthorized access')
        return redirect(url_for('auth_harvest_rig_bp.index'))

    db.session.delete(harvest_rig)
    db.session.commit()
    flash('HarvestRig successfully deleted!')
    return redirect(url_for('auth_harvest_rig_bp.index'))
