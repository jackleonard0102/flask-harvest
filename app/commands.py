import click
from flask.cli import with_appcontext
from app.extensions import db, bcrypt  # Ensure bcrypt is correctly imported
from app.models import User

@click.command('init-db')
@with_appcontext
def init_db():
    try:
        print("Creating database tables...")
        db.create_all()
        print("Database tables created.")
        
        # Check if superadmin already exists
        if User.query.filter_by(username='superadmin').first() is None:
            print("Creating admin user...")
            admin = User(
                username='superadmin',
                email='superadmin@test.com',
                permission=0
            )
            admin.set_password('superadmin')  # Use set_password method to hash the password
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")
            
    except Exception as e:
        print(f"An error occurred: {e}")