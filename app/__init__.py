from flask import Flask, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, csrf, login_manager, migrate

def create_app(config_class: type[Config] = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Flask-Login configuration
    login_manager.login_view = "auth.login" 
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    
    # Import models so SQLAlchemy registers them before creating tables
    from app.models.user import User
    # Import any other model files here so their tables get created as well
    # e.g., from app.models.role import Role
    
    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.user_routes import user_bp
    from app.routes.role_routes import role_bp
    from app.routes.permission_routes import permission_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.fact_routes import fact_bp
    from app.routes.rule_routes import rule_bp
    from app.routes.diagnose_routes import diagnose_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(fact_bp)
    app.register_blueprint(rule_bp)
    app.register_blueprint(diagnose_bp)

    # Smart Root Redirect: Admins go to Users, regular users go to Start Diagnosis
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            if getattr(current_user, 'is_admin', False) or current_user.has_permission("user.view"):
                return redirect(url_for("users.index"))
            return redirect(url_for("diagnose.start"))
        return redirect(url_for("auth.login"))

    # Auto-create all SQLite tables on app startup
    with app.app_context():
        db.create_all()
    
    return app