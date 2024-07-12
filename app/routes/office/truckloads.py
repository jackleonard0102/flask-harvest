from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Truckload, HarvestPerField
from app.extensions import db

office_truckloads_bp = Blueprint('office_truckloads_bp', __name__)

@office_truckloads_bp.route('/office/truckload')
@login_required
def index():
    if current_user.permission != 3:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    truckloads = Truckload.query.filter(
        Truckload.yield_amount.is_(None),
        Truckload.yield_type.is_(None)
    ).all()
    
    return render_template('office/truckloads.html', current_user=current_user, truckloads=truckloads)

@office_truckloads_bp.route('/office/edit_truckload/<int:truckload_id>', methods=['POST'])
@login_required
def edit_truckload(truckload_id):
    truckload = Truckload.query.get_or_404(truckload_id)
    if current_user.permission != 3:
        flash('Unauthorized access')
        return redirect(url_for('office_truckloads_bp.index'))

    yield_amount = request.form['yield_amount']
    yield_type = request.form['yield_type']

    try:
        yield_amount = float(yield_amount)
        if yield_amount < 0:
            raise ValueError("Yield amount cannot be negative.")
    except ValueError as e:
        flash('Invalid yield amount: {}'.format(e))
        return redirect(url_for('office_truckloads_bp.index'))

    if not yield_type or yield_type not in ['bushels', 'pounds', 'tons']:
        flash('Invalid yield type.')
        return redirect(url_for('office_truckloads_bp.index'))

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
    return redirect(url_for('office_truckloads_bp.index'))
