from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import validates
from app.extensions import db, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    @staticmethod
    @db.event.listens_for(db.session, 'before_flush')
    def receive_before_flush(session, flush_context, instances):
        for instance in session.dirty:
            if isinstance(instance, TimestampMixin):
                instance.updated_at = datetime.utcnow()

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        db.session.commit()

class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    permission = db.Column(db.Integer, nullable=False)  # 0: Superadmin, 1: Admin, 2: Subuser
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def verify_password(self, password):
        # Ensure password_hash is not None or empty
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

class Customer(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, nullable=False)  # 0: active, 1: disable
    users = db.relationship('User', backref='customer', lazy=True)

    def soft_delete(self):
        super().soft_delete()
        for user in self.users:
            user.soft_delete()

class Farm(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    fields = db.relationship('FarmField', backref='farm', lazy=True)
    harvests = db.relationship('Harvest', backref='farm', lazy=True)

class FarmField(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    acreage = db.Column(db.String(80), nullable=False)

class Harvest(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    fields = db.relationship('HarvestPerField', backref='harvest', lazy=True)

class HarvestPerField(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    harvest_id = db.Column(db.Integer, db.ForeignKey('harvest.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('farm_field.id'), nullable=False)
    yield_amount = db.Column(db.Float, nullable=False)