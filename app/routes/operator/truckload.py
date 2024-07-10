from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, logout_user, current_user
from app.models import HarvestRig, Customer, Farm , User, Truck, Truckload, HarvestPerField, Harvest, FarmField
from app.extensions import db

operator_truckload_bp = Blueprint('operator_truckload_bp', __name__)

@operator_truckload_bp.route('/truckload')
@login_required
def index():
    if current_user.permission != 2:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    # all farms and farm_ids in current_user's company
    farms = Farm.query.filter_by(company_id = current_user.company_id).all()
    farm_ids = [farm.id for farm in farms]
    
    # all harvests and harvest_ids in current_user's company
    harvests = Harvest.query.filter(Harvest.farm_id.in_(farm_ids)).all()
    harvest_ids = [harvest.id for harvest in harvests]
    harvest_map = {harvest.id: harvest.name for harvest in harvests}
    company_map = {customer.id: customer.name for customer in harvests}

    # all farm fields in current_user's company
    fields = FarmField.query.all()
    field_map = {field.id: field.name for field in fields}
    
    # all harvest_per_field queries of current_user's company in HarvestPerField table
    harvest_per_field = HarvestPerField.query.filter(HarvestPerField.harvest_id.in_(harvest_ids)).all()

    # all trucks in current_user's company
    trucks = Truck.query.filter(Truck.company_id == current_user.company_id).all()
    
    # all harvest rig in current_user's company
    havest_rigs = HarvestRig.query.filter(HarvestRig.company_id == current_user.company_id).all()
    
    return render_template('operator/truckload.html', current_user=current_user, harvest_per_field=harvest_per_field, harvests=harvests, company_map=company_map)

@operator_truckload_bp.route('/logout')
@login_required
def logout():
    rigs = HarvestRig.query.filter_by(current_operator_id=current_user.id).all()
    for rig in rigs:
        rig.current_operator_id = ''
    db.session.commit()

    logout_user()
    return redirect(url_for('main.home'))
