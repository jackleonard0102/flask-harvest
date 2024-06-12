from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Customer
from app.extensions import db
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class CompanyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    status = SelectField('Status', choices=[('active', 'Active'), ('disable', 'Disable')], validators=[DataRequired()])
    submit = SubmitField('Submit')

# Register the blueprint with a unique url_prefix
admin_company_bp = Blueprint('company', __name__, url_prefix='/admin/company')

@admin_company_bp.route('/')
@login_required
def index():
    if current_user.permission not in [0, 1]:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('authentication.login'))
    children = Customer.query.filter(Customer.deleted_at == None).all()
    form = CompanyForm()  # Create instance of form to pass CSRF token
    return render_template('admin/company.html', current_user=current_user, children=children, form=form)

@admin_company_bp.route('/add', methods=['POST'])
@login_required
def add_company():
    if current_user.permission not in [0, 1]:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('authentication.login'))

    form = CompanyForm()
    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        status = form.status.data

        # Check for existing company with the same name that is not soft deleted
        existing_company = Customer.query.filter_by(name=name, deleted_at=None).first()
        if existing_company:
            flash('Company with this name already exists!', 'danger')
        else:
            new_company = Customer(name=name, address=address, status=status)
            db.session.add(new_company)
            db.session.commit()
            flash('Company added successfully', 'success')
    else:
        flash('All fields are required!', 'danger')

    return redirect(url_for('company.index'))

@admin_company_bp.route('/edit/<int:company_id>', methods=['POST'])
@login_required
def edit_company(company_id):
    if current_user.permission not in [0, 1]:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('authentication.login'))

    company = Customer.query.get_or_404(company_id)
    form = CompanyForm()

    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        status = form.status.data

        # Check for existing company with the same name that is not soft deleted
        existing_company = Customer.query.filter(Customer.name == name, Customer.id != company_id, Customer.deleted_at == None).first()
        if existing_company:
            flash('Another company with this name already exists!', 'danger')
        else:
            company.name = name
            company.address = address
            company.status = status
            db.session.commit()
            flash('Company updated successfully', 'success')
    else:
        flash('All fields are required!', 'danger')

    return redirect(url_for('company.index'))

@admin_company_bp.route('/delete/<int:company_id>')
@login_required
def delete_company(company_id):
    if current_user.permission not in [0, 1]:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('authentication.login'))

    company = Customer.query.get(company_id)
    if company:
        company.soft_delete()  # Soft delete the company
        db.session.commit()
        flash('Company deleted successfully', 'success')
        print(f"Company {company_id} soft deleted.")
    else:
        print(f"Company {company_id} not found.")

    return redirect(url_for('company.index'))
