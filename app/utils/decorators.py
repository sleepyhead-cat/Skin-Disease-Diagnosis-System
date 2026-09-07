from functools import wraps
from flask import abort
from flask_login import current_user

def has_permission(permission_code: str):
    """
    Decorator to restrict route access based on specific permission codes.
    Checks if the authenticated user has a role with the required permission.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            # Allow Super Admin / Admin users to bypass permission checks
            if hasattr(current_user, 'is_admin') and current_user.is_admin:
                return f(*args, **kwargs)

            # Extract all permission codes assigned to any of the user's roles
            user_permissions = {
                p.code 
                for role in getattr(current_user, 'roles', []) 
                for p in getattr(role, 'permissions', [])
            }
            
            if permission_code not in user_permissions:
                abort(403)  # Forbidden
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator