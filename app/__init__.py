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
    
    # Import all models before create_all to ensure tables & relationships are registered
    from app.models.user import User
    from app.models.role import Role
    from app.models.permission import Permission
    from app.models.associations import user_roles, role_permissions, user_diagnoses
    
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

    # Auto-create tables and seed initial roles and admin user on startup
    with app.app_context():
        db.create_all()

        # 1. Seed Default Roles
        roles_data = {
            "Admin": "System Administrator with full access.",
            "Doctor": "Medical professional with diagnostic access.",
            "User": "Standard registered user."
        }
        
        roles_map = {}
        for role_name, description in roles_data.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=description)
                db.session.add(role)
            roles_map[role_name] = role
        
        db.session.commit()

        # 2. Seed Default Permissions
        permissions_data = [
            ("user.view", "View users"),
            ("user.manage", "Manage users"),
            ("diagnose.start", "Run skin diagnosis"),
        ]
        
        for code, desc in permissions_data:
            if not Permission.query.filter_by(code=code).first():
                db.session.add(Permission(code=code, description=desc))
        
        db.session.commit()

        # 3. Seed Default Admin User
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="System Administrator",
                phone_number="+10000000000",
                is_active=True
            )
            admin_user.set_password("Admin123!")
            
            # Attach Admin role so user.is_admin evaluates to True
            if "Admin" in roles_map:
                admin_user.roles.append(roles_map["Admin"])

            db.session.add(admin_user)
            db.session.commit()

    return app