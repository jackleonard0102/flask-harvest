import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(INSTANCE_DIR, "yourdatabase.db")}')