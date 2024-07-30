from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Truckload, HarvestPerField
from app.extensions import db

trucker_truckloads_bp = Blueprint('trucker_truckloads_bp', __name__)

@trucker_truckloads_bp.route('/trucker/truckload')
@login_required
def index():
    if current_user.permission != 4:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    truckloads = Truckload.query.filter(
        Truckload.yield_amount.is_(None),
        Truckload.yield_type.is_(None)
    ).all()
    
    return render_template('trucker/truckload.html', current_user=current_user, truckloads=truckloads)

@trucker_truckloads_bp.route('/trucker/edit_truckload/<int:truckload_id>', methods=['POST'])
@login_required
def edit_truckload(truckload_id):
    truckload = Truckload.query.get_or_404(truckload_id)
    if current_user.permission != 4:
        flash('Unauthorized access')
        return redirect(url_for('trucker_truckloads_bp.index'))

    yield_amount = request.form.get('yield_amount', type=float)
    yield_type = request.form.get('yield_type')

    # Validate yield_amount
    if yield_amount is None or yield_amount < 0:
        flash('Invalid yield amount: Must be a non-negative number.')
        return redirect(url_for('trucker_truckloads_bp.index'))

    # Validate yield_type
    if yield_type not in ['bushels', 'pounds', 'tons']:
        flash('Invalid yield type: Must be one of "bushels", "pounds", or "tons".')
        return redirect(url_for('trucker_truckloads_bp.index'))

    # Update Truckload data
    truckload.yield_amount = yield_amount
    truckload.yield_type = yield_type

    # Update HarvestPerField data
    harvest_per_field = HarvestPerField(
        harvest_id=truckload.harvest_id,
        field_id=truckload.field_id,
        yield_amount=yield_amount,
        yield_type=yield_type
    )
    db.session.add(harvest_per_field)

    db.session.commit()
    flash('Truckload successfully updated!')
    return redirect(url_for('trucker_truckloads_bp.index'))
