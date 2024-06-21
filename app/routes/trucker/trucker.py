from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, logout_user, current_user
from app.models import Truck, Customer
from app.extensions import db
from flask import jsonify

trucker_bp = Blueprint('trucker_bp', __name__)

@trucker_bp.route('/trucker')
@login_required
def index():
    if current_user.permission != 4:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    children_1 = Truck.query.filter(
        (Truck.company_id == current_user.company_id) &
        ((Truck.current_driver_id == None) | (Truck.current_driver_id == current_user.id))
    ).all()

    children_2 = Customer.query.filter(
        Customer.deleted_at.is_(None),
        Customer.status == 0,
        Customer.id == current_user.company_id
    ).all()

    # Create a dictionary to map company_id to company.name
    company_map = {customer.id: customer.name for customer in children_2}

    return render_template('trucker/trucker.html', current_user=current_user, children_1=children_1, children_2=children_2, company_map=company_map)

@trucker_bp.route('/select_truck', methods=['POST'])
@login_required
def select_truck():
    if current_user.permission != 4:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    truck_id = request.form['truck_id']
    truck = Truck.query.get_or_404(truck_id)

    # If the truck is already selected by the current user, cancel the selection
    if truck.current_driver_id == current_user.id:
        truck.current_driver_id = None
        message = f'Truck {truck.name} successfully deselected by {current_user.username}!'
    else:
        # Update the truck's current driver to the current user
        truck.current_driver_id = current_user.id
        message = f'Truck {truck.name} successfully selected by {current_user.username}!'

    db.session.commit()
    flash(message)

    return redirect(url_for('trucker_bp.index'))

@trucker_bp.route('/select_truck_ajax', methods=['POST'])
@login_required
def select_truck_ajax():
    if current_user.permission != 4:
        return jsonify({'error': 'Unauthorized access'}), 403

    truck_id = request.form['truck_id']
    truck = Truck.query.get_or_404(truck_id)

    if truck.current_driver_id == current_user.id:
        # If the truck is already selected by the current user, deselect it
        truck.current_driver_id = None
    else:
        # Otherwise, select the truck for the current user
        truck.current_driver_id = current_user.id

    db.session.commit()
    return jsonify({
        'truck_id': truck.id,
        'current_driver_id': truck.current_driver_id,
        'current_driver_name': current_user.username if truck.current_driver_id == current_user.id else ''
    })

@trucker_bp.route('/logout')
@login_required
def logout():
    trucks = Truck.query.filter_by(current_driver_id=current_user.id).all()
    for truck in trucks:
        truck.current_driver_id = None
    db.session.commit()

    logout_user()
    return redirect(url_for('main.home'))
