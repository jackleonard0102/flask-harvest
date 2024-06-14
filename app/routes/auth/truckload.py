from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Truckload
from app.extensions import db

auth_truckload_bp = Blueprint('auth_truckload_bp', __name__)

@auth_truckload_bp.route('/auth/truckload')
@login_required
def index():
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    truckloads = Truckload.query.all()
    
    return render_template('auth/truckload.html', current_user=current_user, truckloads=truckloads)

@auth_truckload_bp.route('/auth/add_truckload_modal', methods=['POST'])
@login_required
def add_truckload_modal():
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    harvest_rig_id = request.form['harvest_rig_id']
    operator_id = request.form['operator_id']
    truck_id = request.form['truck_id']
    trucker_id = request.form['trucker_id']
    field_id = request.form['field_id']
    harvest_id = request.form['harvest_id']
    yield_amount = request.form['yield_amount']
    yield_type = request.form['yield_type']

    if not harvest_rig_id or not operator_id or not truck_id or not trucker_id or not field_id or not harvest_id or not yield_amount or not yield_type:
        flash('All fields are required.')
        return redirect(url_for('auth_truckload_bp.index'))

    new_truckload = Truckload(
        harvest_rig_id=harvest_rig_id,
        operator_id=operator_id,
        truck_id=truck_id,
        trucker_id=trucker_id,
        field_id=field_id,
        harvest_id=harvest_id,
        yield_amount=yield_amount,
        yield_type=yield_type
    )
    db.session.add(new_truckload)
    db.session.commit()
    flash('Truckload successfully added!')
    return redirect(url_for('auth_truckload_bp.index'))

@auth_truckload_bp.route('/auth/edit_truckload/<int:truckload_id>', methods=['POST'])
@login_required
def edit_truckload(truckload_id):
    truckload = Truckload.query.get_or_404(truckload_id)
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('auth_truckload_bp.index'))

    harvest_rig_id = request.form['harvest_rig_id']
    operator_id = request.form['operator_id']
    truck_id = request.form['truck_id']
    trucker_id = request.form['trucker_id']
    field_id = request.form['field_id']
    harvest_id = request.form['harvest_id']
    yield_amount = request.form['yield_amount']
    yield_type = request.form['yield_type']

    if not harvest_rig_id or not operator_id or not truck_id or not trucker_id or not field_id or not harvest_id or not yield_amount or not yield_type:
        flash('All fields are required.')
        return redirect(url_for('auth_truckload_bp.index'))

    truckload.harvest_rig_id = harvest_rig_id
    truckload.operator_id = operator_id
    truckload.truck_id = truck_id
    truckload.trucker_id = trucker_id
    truckload.field_id = field_id
    truckload.harvest_id = harvest_id
    truckload.yield_amount = yield_amount
    truckload.yield_type = yield_type

    db.session.commit()
    flash('Truckload successfully updated!')
    return redirect(url_for('auth_truckload_bp.index'))

@auth_truckload_bp.route('/auth/delete_truckload/<int:truckload_id>')
@login_required
def delete_truckload(truckload_id):
    truckload = Truckload.query.get_or_404(truckload_id)
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('auth_truckload_bp.index'))

    db.session.delete(truckload)
    db.session.commit()
    flash('Truckload successfully deleted!')
    return redirect(url_for('auth_truckload_bp.index'))
