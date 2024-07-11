from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, logout_user, current_user
from app.models import HarvestRig, Customer, Farm, User, Truck, Truckload, HarvestPerField, Harvest, FarmField
from app.extensions import db
from datetime import datetime

operator_truckload_bp = Blueprint('operator_truckload_bp', __name__)

@operator_truckload_bp.route('/truckload', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.permission != 2:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))
    
    unfinished_truckload = Truckload.query.filter(Truckload.trucker_confirmation ==0, Truckload.operator_id == current_user.id).all()
    if unfinished_truckload:
        return redirect(url_for('operator_truckload_bp.show_truckload', truckload_id=unfinished_truckload.id))

    if request.method == 'POST':
        harvest_rig_id = request.form.get('harvest_rig_id')
        harvest_id = request.form.get('harvest')
        field_id = request.form.get('field')
        truck_id = request.form.get('truck')
        trucker_id = request.form.get('trucker')
        load_date_time = request.form.get('load_date_time')

        # Parse the load_date_time to a datetime object
        load_date_time = datetime.strptime(load_date_time, '%Y-%m-%dT%H:%M')
        # load_date_time = load_date_time.replace(second=0, microsecond=0)
        new_truckload = Truckload(
            operator_id=current_user.id,
            harvest_rig_id=harvest_rig_id,
            harvest_id=harvest_id,
            field_id=field_id,
            truck_id=truck_id,
            trucker_id=trucker_id,
            load_date_time=load_date_time,
            trucker_confirmation=0  # Assuming it's not confirmed initially
        )
        db.session.add(new_truckload)
        db.session.commit()
        flash("New truckload created successfully!")
        return redirect(url_for('operator_truckload_bp.show_truckload', truckload_id=new_truckload.id))

    # Data fetching for GET request
    farms = Farm.query.filter_by(company_id=current_user.company_id).all()
    farm_ids = [farm.id for farm in farms]
    
    harvests = Harvest.query.filter(Harvest.farm_id.in_(farm_ids)).all()
    harvests_list = [{'id': harvest.id, 'name': harvest.name, 'farm_id': harvest.farm_id} for harvest in harvests]
    
    fields = FarmField.query.filter(FarmField.farm_id.in_(farm_ids)).all()
    fields_list = [{'id': field.id, 'name': field.name, 'farm_id': field.farm_id} for field in fields]
    
    trucks = Truck.query.filter(Truck.company_id == current_user.company_id, Truck.current_driver_id != "").all()
    trucks_list = [{'id': truck.id, 'name': truck.name, 'current_driver_id': truck.current_driver_id} for truck in trucks]
    
    harvest_rigs = HarvestRig.query.filter_by(company_id=current_user.company_id).all()
    
    truckers = User.query.filter_by(company_id=current_user.company_id).all()
    truckers_list = [{'id': trucker.id, 'username': trucker.username} for trucker in truckers]

    # Fetch the last record of harvest_id and field_id from Truckload table for default values
    last_truckload = Truckload.query.order_by(Truckload.id.desc()).first()
    default_harvest_id = last_truckload.harvest_id if last_truckload else None
    default_field_id = last_truckload.field_id if last_truckload else None
    
    # Get optional harvest_ids from HarvestPerField table
    harvest_per_field_ids = [hpf.harvest_id for hpf in HarvestPerField.query.all()]

    # Fetch harvest names for the dropdown
    harvest_names = {harvest.id: harvest.name for harvest in harvests}
    
    field_names = {field.id: field.name for field in fields}

    # Filter fields based on the last harvest_id
    if default_harvest_id:
        default_harvest = Harvest.query.get(default_harvest_id)
        related_fields = FarmField.query.filter_by(farm_id=default_harvest.farm_id).all()
    else:
        related_fields = fields

    # Determine default truck and trucker for first load
    if trucks_list:
        default_truck_id = trucks_list[0]['id']
        default_trucker_id = trucks_list[0]['current_driver_id'] if trucks_list[0].get('current_driver_id') else None
        default_trucker_name = next((trucker['username'] for trucker in truckers_list if trucker['id'] == default_trucker_id), '')
    else:
        default_truck_id = None
        default_trucker_id = None
        default_trucker_name = ''

    return render_template(
        'operator/truckload.html', 
        current_user=current_user, 
        harvests=harvests_list, 
        fields=fields_list, 
        related_fields=related_fields,
        trucks=trucks_list, 
        harvest_rigs=harvest_rigs, 
        truckers=truckers_list,
        default_harvest_id=default_harvest_id,
        default_field_id=default_field_id,
        default_truck_id=default_truck_id, 
        default_trucker_id=default_trucker_id,
        default_trucker_name=default_trucker_name,
        harvest_per_field_ids=harvest_per_field_ids,
        harvest_names=harvest_names,
        field_names=field_names
    )

@operator_truckload_bp.route('/truckload/in_progress/<int:truckload_id>', methods=['GET'])
@login_required
def show_truckload(truckload_id):
    truckload = Truckload.query.get_or_404(truckload_id)
    return render_template('operator/truckloads.html', truckload=truckload)


@operator_truckload_bp.route('/truckload/finish/<int:truckload_id>', methods=['POST'])
@login_required
def finish_truckload(truckload_id):
    truckload = Truckload.query.get_or_404(truckload_id)
    
    if truckload.trucker_confirmation == 1 and truckload.yield_amount and truckload.yield_type:
        truckload.unload_date_time = datetime.utcnow()
        truckload.trucker_confirmation = 2
        db.session.commit()
        flash("Truckload finished successfully!")
        return redirect(url_for('operator_truckload_bp.index'))
    else:
        flash("Unable to finish current truckload. Ensure trucker confirmation and yield data is present.")
        return redirect(url_for('operator_truckload_bp.show_truckload', truckload_id=truckload.id))

@operator_truckload_bp.route('/truckload/cancel/<int:truckload_id>', methods=['POST'])
@login_required
def cancel_truckload(truckload_id):
    truckload = Truckload.query.get_or_404(truckload_id)
    db.session.delete(truckload)
    db.session.commit()
    flash("Truckload canceled successfully!")
    return redirect(url_for('operator_truckload_bp.index'))

@operator_truckload_bp.route('/logout')
@login_required
def logout():
    rigs = HarvestRig.query.filter_by(current_operator_id=current_user.id).all()
    for rig in rigs:
        rig.current_operator_id = ''
    db.session.commit()

    logout_user()
    return redirect(url_for('main.home'))