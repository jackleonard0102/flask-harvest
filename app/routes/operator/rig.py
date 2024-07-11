from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, logout_user, current_user
from app.models import HarvestRig, Customer, Truckload
from app.extensions import db
from datetime import datetime

operator_rig_bp = Blueprint('operator_rig_bp', __name__)

@operator_rig_bp.route('/harvest_rig')
@login_required
def index():
    if current_user.permission != 2:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    children_1 = HarvestRig.query.filter(
        (HarvestRig.company_id == current_user.company_id) &
        ((HarvestRig.current_operator_id == '') | (HarvestRig.current_operator_id == current_user.id))
    ).all()
    children_2 = Customer.query.filter(
        Customer.deleted_at.is_(None),
        Customer.status == 0,  # Assuming status 0 means 'active'
        Customer.id == current_user.company_id
    ).all()

    # Create a dictionary to map company_id to company.name
    company_map = {customer.id: customer.name for customer in children_2}

    return render_template('operator/rig.html', current_user=current_user, children_1=children_1, children_2=children_2, company_map=company_map)

@operator_rig_bp.route('/select_rig', methods=['POST'])
@login_required
def select_rig():
    if current_user.permission != 2:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    # Check for unfinished truckloads
    unfinished_truckload = Truckload.query.filter(
        Truckload.operator_id == current_user.id,
        db.or_(
            Truckload.trucker_confirmation == 0,
            Truckload.yield_amount == None,
            Truckload.yield_type == None
        )
    ).first()

    # Debug statement
    print(f"Unfinished Truckload: {unfinished_truckload}")

    if unfinished_truckload:
        flash("You have unfinished truckloads. Please complete them before selecting a new rig.")
        return redirect(url_for('operator_truckload_bp.show_truckload', truckload_id=unfinished_truckload.id))

    rig_id = request.form['rig_id']
    rig = HarvestRig.query.get_or_404(rig_id)

    # If the rig is already selected by the current user, cancel the selection
    if rig.current_operator_id == current_user.id:
        rig.current_operator_id = ''
        message = f'Rig {rig.name} successfully deselected by {current_user.username}!'
    else:
        # Update the rig's current operator to the current user
        rig.current_operator_id = current_user.id
        message = f'Rig {rig.name} successfully selected by {current_user.username}!'

    db.session.commit()
    flash(message)

    return redirect(url_for('operator_rig_bp.index'))

@operator_rig_bp.route('/select_rig_ajax', methods=['POST'])
@login_required
def select_rig_ajax():
    if current_user.permission != 2:
        return jsonify({'error': 'Unauthorized access'}), 403

    # Check for unfinished truckloads
    unfinished_truckload = Truckload.query.filter(
        Truckload.operator_id == current_user.id,
        db.or_(
            Truckload.trucker_confirmation == 0,
            Truckload.yield_amount == None,
            Truckload.yield_type == None
        )
    ).first()

    # Debug statement
    print(f"Unfinished Truckload (AJAX): {unfinished_truckload}")

    if unfinished_truckload:
        return jsonify({'error': 'You have unfinished truckloads. Please complete them before selecting a new rig.'}), 403

    rig_id = request.form['rig_id']
    rig = HarvestRig.query.get_or_404(rig_id)

    if rig.current_operator_id == current_user.id:
        # If the rig is already selected by the current user, deselect it
        rig.current_operator_id = ''
    else:
        # Otherwise, select the rig for the current user
        rig.current_operator_id = current_user.id

    db.session.commit()
    return jsonify({
        'rig_id': rig.id,
        'current_operator_id': rig.current_operator_id,
        'current_operator_name': current_user.username if rig.current_operator_id == current_user.id else ''
    })

@operator_rig_bp.route('/logout')
@login_required
def logout():
    rigs = HarvestRig.query.filter_by(current_operator_id=current_user.id).all()
    for rig in rigs:
        rig.current_operator_id = ''
    db.session.commit()

    logout_user()
    return redirect(url_for('main.home'))
