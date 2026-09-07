from typing import List, Optional
from app.models.permission import Permission
from extensions import db

class PermissionService:
    @staticmethod
    def get_permission_all() -> List[Permission]:
        return Permission.query.order_by(Permission.id.asc()).all()
    
    @staticmethod
    def get_permission_by_id(permission_id: int) -> Optional[Permission]:
        return Permission.query.get(permission_id)
    
    @staticmethod
    def create_permission(data: dict) -> Permission:
        perm = Permission(
            code=data["code"],
            name=data["name"],
            module=data.get("module", "General"),
            description=data.get("description") or "",
        )
        db.session.add(perm)
        db.session.commit()
        return perm
    
    @staticmethod
    def update_permission(permission: Permission, data: dict,) -> Permission:
        permission.code = data["code"]
        permission.name = data["name"]
        permission.module = data.get("module", "General")
        permission.description = data.get("description") or ""
        
        db.session.commit()
        return permission
    
    @staticmethod
    def delete_permission(permission: Permission) -> None:
        db.session.delete(permission)
        db.session.commit()
        