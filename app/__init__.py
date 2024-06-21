import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from .extensions import bcrypt, db, login_manager
from .admin import setup_admin
from .commands import init_db
from app.models import User
from app.routes.authentication import auth_bp
from app.routes.main import main_bp
from app.routes.admin.company import admin_company_bp
from app.routes.admin.user import admin_user_bp
from app.routes.admin.farm import admin_farm_bp
from app.routes.admin.field import admin_field_bp
from app.routes.admin.harvest import admin_harvest_bp
from app.routes.admin.harvest_per_field import admin_harvest_per_field_bp
from app.routes.admin.truck import admin_truck_bp
from app.routes.admin.truckload import admin_truckload_bp
from app.routes.admin.harvest_rig import admin_harvest_rig_bp
from app.routes.auth.user import auth_user_bp
from app.routes.auth.farm import auth_farm_bp
from app.routes.auth.field import auth_field_bp
from app.routes.auth.harvest import auth_harvest_bp
from app.routes.auth.harvest_per_field import auth_harvest_per_field_bp
from app.routes.auth.truck import auth_truck_bp
from app.routes.auth.truckload import auth_truckload_bp
from app.routes.auth.harvest_rig import auth_harvest_rig_bp
from app.routes.trucker.trucker import trucker_bp
from app.routes.operator.rig import operator_rig_bp

migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('../config.py')

    # Ensure the 'instance' directory exists
    instance_path = app.instance_path
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    # Add debug statements
    print(f"Base Directory: {os.path.abspath(os.path.dirname(__file__))}")
    print(f"Instance Directory: {instance_path}")
    db_path = os.path.join(instance_path, "yourdatabase.db")
    print(f"Database Path: {db_path}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Verify directory and file permissions
    if not os.access(instance_path, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {instance_path}")

    if not os.access(db_path, os.F_OK):
        print("Database file does not exist yet.")
    elif not os.access(db_path, os.W_OK):
        raise PermissionError(f"Cannot write to database file: {db_path}")
    
    Bootstrap(app)
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Setup LoginManager
    login_manager.login_view = 'authentication.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    app.register_blueprint(admin_company_bp)
    app.register_blueprint(admin_user_bp)
    app.register_blueprint(admin_farm_bp)
    app.register_blueprint(admin_field_bp)
    app.register_blueprint(admin_harvest_bp)
    app.register_blueprint(admin_harvest_per_field_bp)
    app.register_blueprint(admin_truck_bp)
    app.register_blueprint(admin_harvest_rig_bp)
    app.register_blueprint(admin_truckload_bp)
    
    app.register_blueprint(auth_user_bp)
    app.register_blueprint(auth_farm_bp)
    app.register_blueprint(auth_field_bp)
    app.register_blueprint(auth_harvest_bp)
    app.register_blueprint(auth_harvest_per_field_bp)
    app.register_blueprint(auth_truck_bp)
    app.register_blueprint(auth_harvest_rig_bp)
    app.register_blueprint(auth_truckload_bp)
    
    app.register_blueprint(trucker_bp)
    app.register_blueprint(operator_rig_bp)
    
    app.cli.add_command(init_db)
    setup_admin(app, db)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
