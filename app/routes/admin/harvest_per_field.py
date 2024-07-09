from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app.models import HarvestPerField, Harvest, FarmField, Customer, Farm
from app.extensions import db

admin_harvest_per_field_bp = Blueprint('admin_harvest_per_field_bp', __name__)

@admin_harvest_per_field_bp.route('/admin/harvest_per_field')
@login_required
def index():
    if current_user.permission != 0: 
        flash('Unauthorized access')
        return redirect(url_for('main.home'))
    active_customer_ids = [customer.id for customer in Customer.query.filter(Customer.deleted_at == None, Customer.status == 'active').all()]
    farms = Farm.query.join(Customer, Customer.status == "active").filter(Farm.deleted_at == None, Farm.company_id.in_(active_customer_ids)).all()
    active_farm_ids = [farm.id for farm in farms]
    farm_fields = FarmField.query.filter(FarmField.farm_id.in_(active_farm_ids)).all()
    active_farm_fields = [field.id for field in farm_fields]
    
    harvests = Harvest.query.filter(Harvest.farm_id.in_(active_farm_ids)).all()
    children_1 = HarvestPerField.query.filter(HarvestPerField.field_id.in_(active_farm_fields)).all()
    
    # Create dictionaries to map harvest_id and field_id to their names
    harvest_map = {harvest.id: harvest.name for harvest in harvests}
    field_map = {field.id: field.name for field in farm_fields}
    
    return render_template('admin/harvest_per_field.html', current_user=current_user, children_1=children_1, harvest_map=harvest_map, field_map=field_map, harvests=harvests, farm_fields=active_farm_fields)

@admin_harvest_per_field_bp.route('/add_harvest_per_field_modal', methods=['POST'])
@login_required
def add_harvest_per_field_modal():
    if current_user.permission != 0:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    harvest_id = request.form['harvest_id']
    field_id = request.form['field_id']
    yield_amount = request.form.get('yield_amount')
    yield_type = request.form.get('yield_type')

    # Validate inputs
    if not harvest_id or not field_id:
        flash('Harvest and Field are required.')
        return redirect(url_for('admin_harvest_per_field_bp.index'))

    # Set default values if not provided
    if not yield_amount:
        yield_amount = 0.0
    else:
        try:
            yield_amount = float(yield_amount)
        except ValueError:
            flash('Yield amount must be a valid number.')
            return redirect(url_for('admin_harvest_per_field_bp.index'))

    new_harvest_per_field = HarvestPerField(
        harvest_id=harvest_id,
        field_id=field_id,
        yield_amount=yield_amount,
        yield_type=yield_type
    )
    db.session.add(new_harvest_per_field)
    db.session.commit()
    flash('Harvest Per Field successfully added!')
    return redirect(url_for('admin_harvest_per_field_bp.index'))

@admin_harvest_per_field_bp.route('/edit_harvest_per_field/<int:harvest_per_field_id>', methods=['POST'])
@login_required
def edit_harvest_per_field(harvest_per_field_id):
    harvest_per_field = HarvestPerField.query.get_or_404(harvest_per_field_id)
    if current_user.permission != 0:  # Only superadmin or admin can edit harvest per fields
        flash('Unauthorized access')
        return redirect(url_for('admin_harvest_per_field_bp.index'))

    harvest_id = request.form['harvest_id']
    field_id = request.form['field_id']
    yield_amount = request.form.get('yield_amount')
    yield_type = request.form.get('yield_type')

    # Validate inputs
    if not harvest_id or not field_id:
        flash('Harvest and Field are required.')
        return redirect(url_for('admin_harvest_per_field_bp.index'))

    # Set default values if not provided
    if not yield_amount:
        yield_amount = 0.0
    else:
        try:
            yield_amount = float(yield_amount)
        except ValueError:
            flash('Yield amount must be a valid number.')
            return redirect(url_for('admin_harvest_per_field_bp.index'))

    harvest_per_field.harvest_id = harvest_id
    harvest_per_field.field_id = field_id
    harvest_per_field.yield_amount = yield_amount
    harvest_per_field.yield_type = yield_type

    db.session.commit()
    flash('Harvest Per Field successfully updated!')
    return redirect(url_for('admin_harvest_per_field_bp.index'))

@admin_harvest_per_field_bp.route('/delete_harvest_per_field/<int:harvest_per_field_id>')
@login_required
def delete_harvest_per_field(harvest_per_field_id):
    harvest_per_field = HarvestPerField.query.get_or_404(harvest_per_field_id)
    if current_user.permission != 0:  # Only superadmin or admin can delete harvest per fields
        flash('Unauthorized access')
        return redirect(url_for('admin_harvest_per_field_bp.index'))

    db.session.delete(harvest_per_field)
    db.session.commit()
    flash('Harvest Per Field successfully deleted!')
    return redirect(url_for('admin_harvest_per_field_bp.index'))

@admin_harvest_per_field_bp.route('/get_fields_by_harvest', methods=['GET'])
def get_fields_by_harvest():
    harvest_id = request.args.get('harvest_id')
    if harvest_id:
        harvest = Harvest.query.get(harvest_id)
        if harvest:
            fields = FarmField.query.filter_by(farm_id=harvest.farm_id).all()
            fields_data = [{'id': field.id, 'name': field.name} for field in fields]
            return jsonify({'fields': fields_data})
    return jsonify({'fields': []})
