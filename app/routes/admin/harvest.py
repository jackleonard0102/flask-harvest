from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Harvest, Farm, Customer
from app.extensions import db
from datetime import datetime

admin_harvest_bp = Blueprint('admin_harvest_bp', __name__)

@admin_harvest_bp.route('/admin/harvest')
@login_required
def index():
    if current_user.permission != 0:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    active_customer_ids = [customer.id for customer in Customer.query.filter(Customer.deleted_at == None, Customer.status == 'active').all()]
    farms = Farm.query.join(Customer, Customer.status == "active").filter(Farm.deleted_at == None, Farm.company_id.in_(active_customer_ids)).all()
    active_farm_ids = [farm.id for farm in farms]
    harvests = Harvest.query.filter(Harvest.farm_id.in_(active_farm_ids)).all()
    
    # Create a dictionary to map farm_id to farm.name
    farm_map = {farm.id: farm.name for farm in farms}
    
    return render_template('admin/harvest.html', current_user=current_user, harvests=harvests, farm_map=farm_map, farms=farms)

@admin_harvest_bp.route('/add_harvest_modal', methods=['POST'])
@login_required
def add_harvest_modal():
    if current_user.permission != 0:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    name = request.form['name']
    date = request.form['date']
    farm_id = request.form['farm_id']

    # Validate inputs
    if not name or not date or not farm_id:
        flash('All fields are required.')
        return redirect(url_for('admin_harvest_bp.index'))

    new_harvest = Harvest(
        name=name,
        date=datetime.strptime(date, '%Y-%m-%d'),
        farm_id=farm_id
    )
    db.session.add(new_harvest)
    db.session.commit()
    flash('Harvest successfully added!')
    return redirect(url_for('admin_harvest_bp.index'))


@admin_harvest_bp.route('/edit_harvest/<int:harvest_id>', methods=['POST'])
@login_required
def edit_harvest(harvest_id):
    harvest = Harvest.query.get_or_404(harvest_id)
    if current_user.permission != 0:  # Only superadmin or admin can edit harvests
        flash('Unauthorized access')
        return redirect(url_for('admin_harvest_bp.index'))

    name = request.form['name']
    date = request.form['date']
    farm_id = request.form['farm_id']

    # Validate inputs
    if not name or not date or not farm_id:
        flash('All fields are required.')
        return redirect(url_for('admin_harvest_bp.index'))

    harvest.name = name
    harvest.date = datetime.strptime(date, '%Y-%m-%d')
    harvest.farm_id = farm_id

    db.session.commit()
    flash('Harvest successfully updated!')
    return redirect(url_for('admin_harvest_bp.index'))

@admin_harvest_bp.route('/delete_harvest/<int:harvest_id>')
@login_required
def delete_harvest(harvest_id):
    harvest = Harvest.query.get_or_404(harvest_id)
    if current_user.permission != 0:  # Only superadmin or admin can delete harvests
        flash('Unauthorized access')
        return redirect(url_for('admin_harvest_bp.index'))

    db.session.delete(harvest)
    db.session.commit()
    flash('Harvest successfully deleted!')
    return redirect(url_for('admin_harvest_bp.index'))