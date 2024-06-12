from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import HarvestPerField, Harvest, FarmField
from app.extensions import db

admin_harvest_per_field_bp = Blueprint('admin_harvest_per_field_bp', __name__)

@admin_harvest_per_field_bp.route('/admin/harvest_per_field')
@login_required
def index():
    if current_user.permission not in [0, 1]:  # Suppose 0 and 1 are permissions for superadmin and admin
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    children_1 = HarvestPerField.query.all()
    children_2 = Harvest.query.all()
    children_3 = FarmField.query.all()
    
    # Create dictionaries to map harvest_id and field_id to their names
    harvest_map = {harvest.id: harvest.name for harvest in children_2}
    field_map = {field.id: field.name for field in children_3}
    
    return render_template('admin/harvest_per_field.html', current_user=current_user, children_1=children_1, harvest_map=harvest_map, field_map=field_map, children_2=children_2, children_3=children_3)

@admin_harvest_per_field_bp.route('/add_harvest_per_field_modal', methods=['POST'])
@login_required
def add_harvest_per_field_modal():
    if current_user.permission not in [0, 1]:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    harvest_id = request.form['harvest_id']
    field_id = request.form['field_id']
    yield_amount = request.form['yield_amount']

    # Validate inputs
    if not harvest_id or not field_id or not yield_amount:
        flash('All fields are required.')
        return redirect(url_for('admin_harvest_per_field_bp.index'))

    new_harvest_per_field = HarvestPerField(
        harvest_id=harvest_id,
        field_id=field_id,
        yield_amount=yield_amount
    )
    db.session.add(new_harvest_per_field)
    db.session.commit()
    flash('Harvest Per Field successfully added!')
    return redirect(url_for('admin_harvest_per_field_bp.index'))


@admin_harvest_per_field_bp.route('/edit_harvest_per_field/<int:harvest_per_field_id>', methods=['POST'])
@login_required
def edit_harvest_per_field(harvest_per_field_id):
    harvest_per_field = HarvestPerField.query.get_or_404(harvest_per_field_id)
    if current_user.permission not in [0, 1]:  # Only superadmin or admin can edit harvest per fields
        flash('Unauthorized access')
        return redirect(url_for('admin_harvest_per_field_bp.index'))

    harvest_id = request.form['harvest_id']
    field_id = request.form['field_id']
    yield_amount = request.form['yield_amount']

    # Validate inputs
    if not harvest_id or not field_id or not yield_amount:
        flash('All fields are required.')
        return redirect(url_for('admin_harvest_per_field_bp.index'))

    harvest_per_field.harvest_id = harvest_id
    harvest_per_field.field_id = field_id
    harvest_per_field.yield_amount = yield_amount

    db.session.commit()
    flash('Harvest Per Field successfully updated!')
    return redirect(url_for('admin_harvest_per_field_bp.index'))

@admin_harvest_per_field_bp.route('/delete_harvest_per_field/<int:harvest_per_field_id>')
@login_required
def delete_harvest_per_field(harvest_per_field_id):
    harvest_per_field = HarvestPerField.query.get_or_404(harvest_per_field_id)
    if current_user.permission not in [0, 1]:  # Only superadmin or admin can delete harvest per fields
        flash('Unauthorized access')
        return redirect(url_for('admin_harvest_per_field_bp.index'))

    db.session.delete(harvest_per_field)
    db.session.commit()
    flash('Harvest Per Field successfully deleted!')
    return redirect(url_for('admin_harvest_per_field_bp.index'))