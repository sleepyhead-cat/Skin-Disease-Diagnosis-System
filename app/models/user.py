from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db
from app.models.associations import user_roles, user_diagnoses

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    roles = db.relationship("Role", secondary=user_roles, back_populates="users")
    diagnoses = db.relationship("Diagnose", secondary=user_diagnoses, back_populates="users")
    
    # Password helpers
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    # Role & permission helpers
    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)
    
    def get_permission_codes(self) -> set[str]:
        return {perm.code for role in self.roles for perm in getattr(role, 'permissions', [])}
    
    @property
    def permissions_codes(self) -> set[str]:
        """Property alias for template usage like current_user.permissions_codes."""
        return self.get_permission_codes()

    @property
    def is_admin(self) -> bool:
        """Quick check if the user has system administrator privileges."""
        return self.has_role("Admin")
    
    def has_permission(self, permission_code: str) -> bool:
        return self.is_admin or (permission_code in self.get_permission_codes())
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"