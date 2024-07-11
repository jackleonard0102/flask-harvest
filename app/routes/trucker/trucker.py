from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, logout_user, current_user
from app.models import Truck, Customer, Truckload
from app.extensions import db

trucker_bp = Blueprint('trucker_bp', __name__)

@trucker_bp.route('/trucker')
@login_required
def index():
    if current_user.permission != 4:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    children_1 = Truck.query.filter(
        (Truck.company_id == current_user.company_id) &
        ((Truck.current_driver_id == '') | (Truck.current_driver_id == current_user.id))
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
        truck.current_driver_id = ''
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

    # If the truck is already selected by the current user, cancel the selection
    if truck.current_driver_id == current_user.id:
        truck.current_driver_id = ''
        message = f'Truck {truck.name} successfully deselected by {current_user.username}!'
    else:
        # Update the truck's current driver to the current user
        truck.current_driver_id = current_user.id
        message = f'Truck {truck.name} successfully selected by {current_user.username}!'

    db.session.commit()
    return jsonify({'message': message, 'truck_id': truck.id, 'current_driver_name': current_user.username})

@trucker_bp.route('/check_unconfirmed_truckloads', methods=['GET'])
@login_required
def check_unconfirmed_truckloads():
    truckload = Truckload.query.filter_by(trucker_id=current_user.id, trucker_confirmation=0).first()

    if truckload:
        return jsonify({'unconfirmed': True, 'truckload_id': truckload.id})
    else:
        return jsonify({'unconfirmed': False})

@trucker_bp.route('/confirm_truckload', methods=['POST'])
@login_required
def confirm_truckload():
    data = request.get_json()
    truckload_id = data.get('truckload_id')
    truckload = Truckload.query.get_or_404(truckload_id)

    if truckload.trucker_id == current_user.id:
        truckload.trucker_confirmation = 1
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Unauthorized access'}), 403
