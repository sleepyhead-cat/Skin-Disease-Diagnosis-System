from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate

migrate = Migrate()
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()