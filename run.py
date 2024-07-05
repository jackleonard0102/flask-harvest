from flask_migrate import Migrate
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)  # Initialize Flask-Migrate with your Flask app and database instance

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
