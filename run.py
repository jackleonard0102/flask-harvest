from flask_migrate import Migrate
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)  # Initialize Flask-Migrate with your Flask app and database instance

if __name__ == '__main__':
    app.run(debug=True)
