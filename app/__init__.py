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
    
    # --- IMPORT ALL MODELS TO REGISTER SCHEMA ---
    from app.models.user import User
    from app.models.role import Role
    from app.models.permission import Permission
    from app.models.fact import Fact
    from app.models.diagnose import Diagnose
    # Import association tables and other rule models if applicable
    from app.models.associations import user_roles, role_permissions, diagnose_rules, user_diagnoses
    
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
            return redirect(url_for("diagnoses.dashboard"))
        return redirect(url_for("auth.login"))

    # --- AUTO-CREATE TABLES & SEED DATABASE ---
    # --- AUTO-CREATE TABLES & SEED DATABASE ---
    with app.app_context():
        db.create_all()

        # 1. Seed Roles
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

        # 2. Seed Permissions
        permissions_data = [
            ("user.view", "View Users", "Allows viewing user list and details", "User Management"),
            ("user.manage", "Manage Users", "Allows creating, editing, and deleting users", "User Management"),
            ("role.view", "View Roles", "Allows viewing roles", "Access Control"),
            ("role.manage", "Manage Roles", "Allows editing roles and permissions", "Access Control"),
            ("diagnose.start", "Run Diagnosis", "Allows running the diagnostic inference engine", "Diagnosis"),
            ("fact.manage", "Manage Facts", "Allows managing medical symptom facts", "Knowledge Base"),
            ("rule.manage", "Manage Rules", "Allows managing expert system rules", "Knowledge Base"),
        ]
        
        all_permissions = []
        for code, name, desc, module in permissions_data:
            perm = Permission.query.filter_by(code=code).first()
            if not perm:
                perm = Permission(code=code, name=name, description=desc, module=module)
                db.session.add(perm)
            all_permissions.append(perm)
        
        db.session.commit()

        # 3. Assign All Permissions to Admin Role
        admin_role = roles_map.get("Admin")
        if admin_role:
            for perm in all_permissions:
                if perm not in admin_role.permissions:
                    admin_role.permissions.append(perm)
            db.session.commit()

        # 4. Seed Admin User
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
            
            if admin_role:
                admin_user.roles.append(admin_role)

            db.session.add(admin_user)
            
        # 5. Seed Second Admin User
        admin_user2 = User.query.filter_by(username="admin2").first()
        if not admin_user2:
            admin_user2 = User(
                username="admin2",
                email="admin2@example.com",
                full_name="Secondary Administrator",
                phone_number="+10000000002",
                is_active=True
            )
            admin_user2.set_password("Admin123!")
            
            if admin_role:
                admin_user2.roles.append(admin_role)

            db.session.add(admin_user2)

        # 5. Seed Standard User
        standard_role = roles_map.get("User")
        normal_user = User.query.filter_by(username="john_doe").first()
        if not normal_user:
            normal_user = User(
                username="john_doe",
                email="john@example.com",
                full_name="John Doe",
                phone_number="+10000000001",
                is_active=True
            )
            normal_user.set_password("User123!")
            
            if standard_role:
                normal_user.roles.append(standard_role)

            db.session.add(normal_user)

        db.session.commit()

    return app