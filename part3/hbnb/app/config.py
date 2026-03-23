import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    # Use absolute path for database in the instance directory
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_dir = os.path.join(basedir, 'instance')
    
    # Ensure the instance directory exists
    os.makedirs(db_dir, exist_ok=True)
    
    # Use forward slashes for SQLite URI
    db_path = os.path.join(db_dir, 'development.db').replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}