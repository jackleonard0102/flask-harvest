from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app.models import HarvestPerField, Harvest, FarmField, Farm
from app.extensions import db

auth_harvest_per_field_bp = Blueprint('auth_harvest_per_field_bp', __name__)

@auth_harvest_per_field_bp.route('/auth/harvest_per_field')
@login_required
def index():
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    farms = Farm.query.filter_by(company_id=current_user.company_id).all()
    farm_ids = [farm.id for farm in farms]

    children_2 = Harvest.query.filter(Harvest.farm_id.in_(farm_ids)).all()
    children_2_ids = [harvest.id for harvest in children_2]

    children_1 = HarvestPerField.query.filter(HarvestPerField.harvest_id.in_(children_2_ids)).all()

    children_3 = FarmField.query.all()

    harvest_map = {harvest.id: harvest.name for harvest in children_2}
    field_map = {field.id: field.name for field in children_3}

    return render_template('auth/harvest_per_field.html', current_user=current_user, children_1=children_1, harvest_map=harvest_map, field_map=field_map, children_2=children_2, children_3=children_3)

@auth_harvest_per_field_bp.route('/auth/add_harvest_per_field_modal', methods=['POST'])
@login_required
def add_harvest_per_field_modal():
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    harvest_id = request.form['harvest_id']
    field_id = request.form['field_id']
    yield_amount = request.form.get('yield_amount')
    yield_type = request.form.get('yield_type')

    if not harvest_id or not field_id:
        flash('Harvest and Field are required.')
        return redirect(url_for('auth_harvest_per_field_bp.index'))

    if not yield_amount:
        yield_amount = 0.0
    else:
        try:
            yield_amount = float(yield_amount)
            if yield_amount < 0:
                flash('Yield amount cannot be negative.')
                return redirect(url_for('auth_harvest_per_field_bp.index'))
        except ValueError:
            flash('Yield amount must be a valid number.')
            return redirect(url_for('auth_harvest_per_field_bp.index'))

    new_harvest_per_field = HarvestPerField(
        harvest_id=harvest_id,
        field_id=field_id,
        yield_amount=yield_amount,
        yield_type=yield_type
    )
    db.session.add(new_harvest_per_field)
    db.session.commit()
    flash('Harvest Per Field successfully added!')
    return redirect(url_for('auth_harvest_per_field_bp.index'))

@auth_harvest_per_field_bp.route('/edit_harvest_per_field/<int:harvest_per_field_id>', methods=['POST'])
@login_required
def edit_harvest_per_field(harvest_per_field_id):
    harvest_per_field = HarvestPerField.query.get_or_404(harvest_per_field_id)
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('auth_harvest_per_field_bp.index'))

    harvest_id = request.form['harvest_id']
    field_id = request.form['field_id']
    yield_amount = request.form.get('yield_amount')
    yield_type = request.form.get('yield_type')

    if not harvest_id or not field_id:
        flash('Harvest and Field are required.')
        return redirect(url_for('auth_harvest_per_field_bp.index'))

    if not yield_amount:
        yield_amount = 0.0
    else:
        try:
            yield_amount = float(yield_amount)
            if yield_amount < 0:
                flash('Yield amount cannot be negative.')
                return redirect(url_for('auth_harvest_per_field_bp.index'))
        except ValueError:
            flash('Yield amount must be a valid number.')
            return redirect(url_for('auth_harvest_per_field_bp.index'))

    harvest_per_field.harvest_id = harvest_id
    harvest_per_field.field_id = field_id
    harvest_per_field.yield_amount = yield_amount
    harvest_per_field.yield_type = yield_type

    db.session.commit()
    flash('Harvest Per Field successfully updated!')
    return redirect(url_for('auth_harvest_per_field_bp.index'))

@auth_harvest_per_field_bp.route('/delete_harvest_per_field/<int:harvest_per_field_id>', methods=['POST'])
@login_required
def delete_harvest_per_field(harvest_per_field_id):
    harvest_per_field = HarvestPerField.query.get_or_404(harvest_per_field_id)
    if current_user.permission != 1:
        flash('Unauthorized access')
        return redirect(url_for('auth_harvest_per_field_bp.index'))

    db.session.delete(harvest_per_field)
    db.session.commit()
    flash('Harvest Per Field successfully deleted!')
    return redirect(url_for('auth_harvest_per_field_bp.index'))

@auth_harvest_per_field_bp.route('/auth/get_fields_by_harvest', methods=['GET'])
def get_fields_by_harvest():
    harvest_id = request.args.get('harvest_id')
    if harvest_id:
        harvest = Harvest.query.get(harvest_id)
        if harvest:
            fields = FarmField.query.filter_by(farm_id=harvest.farm_id).all()
            fields_data = [{'id': field.id, 'name': field.name} for field in fields]
            return jsonify({'fields': fields_data}), 200
    return jsonify({'error': 'Harvest not found'}), 404
