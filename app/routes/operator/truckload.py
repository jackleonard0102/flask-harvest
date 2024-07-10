from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, logout_user, current_user
from app.models import HarvestRig, Customer, Farm, User, Truck, Truckload, HarvestPerField, Harvest, FarmField
from app.extensions import db

operator_truckload_bp = Blueprint('operator_truckload_bp', __name__)

@operator_truckload_bp.route('/truckload', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.permission != 2:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        harvest_rig_id = request.form.get('harvest_rig_id')
        harvest_id = request.form.get('harvest')
        field_id = request.form.get('field')
        truck_id = request.form.get('truck')
        trucker_id = request.form.get('trucker')

        new_truckload = Truckload(
            operator_id=current_user.id,
            harvest_rig_id=harvest_rig_id,
            harvest_id=harvest_id,
            field_id=field_id,
            truck_id=truck_id,
            trucker_id=trucker_id,
            trucker_confirmation=0  # Assuming it's not confirmed initially
        )
        db.session.add(new_truckload)
        db.session.commit()
        flash("New truckload created successfully!")
        return redirect(url_for('operator_truckload_bp.index'))

    # Data fetching for GET request
    farms = Farm.query.filter_by(company_id=current_user.company_id).all()
    farm_ids = [farm.id for farm in farms]
    
    harvests = Harvest.query.filter(Harvest.farm_id.in_(farm_ids)).all()
    
    fields = FarmField.query.filter(FarmField.farm_id.in_(farm_ids)).all()
    
    trucks = Truck.query.filter(Truck.company_id ==current_user.company_id, Truck.current_driver_id != "").all()
   
    harvest_rigs = HarvestRig.query.filter_by(company_id=current_user.company_id).all()
    
    truckers = User.query.filter_by(company_id=current_user.company_id).all()
    
    # Fetch the last record of harvest_id from Truckload table for default value
    last_truckload = Truckload.query.order_by(Truckload.id.desc()).first()
    default_harvest_id = last_truckload.harvest_id if last_truckload else None
    # Get optional harvest_ids from HarvestPerField table
    harvest_per_field_ids = [hpf.harvest_id for hpf in HarvestPerField.query.all()]
    # Fetch harvest names for the dropdown
    harvest_names = {harvest.id: harvest.name for harvest in harvests}

    return render_template(
        'operator/truckload.html', 
        current_user=current_user, 
        harvests=harvests, 
        fields=fields, 
        trucks=trucks, 
        harvest_rigs=harvest_rigs, 
        truckers=truckers,
        default_harvest_id=default_harvest_id,
        harvest_per_field_ids=harvest_per_field_ids,
        harvest_names=harvest_names
    )

@operator_truckload_bp.route('/logout')
@login_required
def logout():
    rigs = HarvestRig.query.filter_by(current_operator_id=current_user.id).all()
    for rig in rigs:
        rig.current_operator_id = ''
    db.session.commit()

    logout_user()
    return redirect(url_for('main.home'))