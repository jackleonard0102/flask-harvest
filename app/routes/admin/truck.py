from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Truck, Customer, User
from app.extensions import db

admin_truck_bp = Blueprint('admin_truck_bp', __name__)

@admin_truck_bp.route('/admin/truck')
@login_required
def index():
    if current_user.permission != 0:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    trucks = Truck.query.all()
    companies = Customer.query.filter(Customer.deleted_at.is_(None), Customer.status == 'active').all()
    truckers = User.query.filter(User.permission == 4).all()
    
    # Create a dictionary to map company_id to company.name
    company_map = {customer.id: customer.name for customer in companies}
    
    return render_template('admin/truck.html', current_user=current_user, trucks=trucks, companies=companies, truckers=truckers, company_map=company_map)


@admin_truck_bp.route('/add_truck_modal', methods=['POST'])
@login_required
def add_truck_modal():
    if current_user.permission != 0:
        flash('Unauthorized access')
        return redirect(url_for('main.home'))

    company_id = request.form['company_id']
    name = request.form['name']
    year = request.form['year']
    vin = request.form['vin']
    driver = request.form['driver']

    if not name or not year or not vin:
        flash('All fields are required.')
        return redirect(url_for('admin_truck_bp.index'))

    new_truck = Truck(
        name=name,
        year=year,
        vin=vin,
        current_driver_id=driver,
        company_id=company_id
    )
    db.session.add(new_truck)
    db.session.commit()
    flash('Truck successfully added!')
    return redirect(url_for('admin_truck_bp.index'))


@admin_truck_bp.route('/edit_truck/<int:truck_id>', methods=['POST'])
@login_required
def edit_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    if current_user.permission != 0:  
        flash('Unauthorized access')
        return redirect(url_for('admin_truck_bp.index'))

    name = request.form['name']
    year = request.form['year']
    vin = request.form['vin']
    driver = request.form['driver']

    if not name or not year or not vin:
        flash('All fields are required.')
        return redirect(url_for('admin_truck_bp.index'))

    truck.name = name
    truck.year = year
    truck.vin = vin
    truck.current_driver_id = driver

    db.session.commit()
    flash('Truck successfully updated!')
    return redirect(url_for('admin_truck_bp.index'))


@admin_truck_bp.route('/delete_truck/<int:truck_id>')
@login_required
def delete_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    if current_user.permission != 0:  
        flash('Unauthorized access')
        return redirect(url_for('admin_truck_bp.index'))

    db.session.delete(truck)
    db.session.commit()
    flash('Truck successfully deleted!')
    return redirect(url_for('admin_truck_bp.index'))
