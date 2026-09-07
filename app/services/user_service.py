from typing import List, Optional
from app.models.user import User
from app.models.role import Role
from extensions import db

class UserService:
    @staticmethod
    def get_user_all() -> List[User]:
        return User.query.order_by(User.id.desc()).all()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        return User.query.get(user_id)
    
    @staticmethod
    def create_user(data: dict, password: str, role_id: Optional[int] = None,) -> User:
        user = User(
            picture=data["picture"],
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            phone_number=data["phone_number"],
            is_active=data.get("is_active", True),
        )
        user.set_password(password)
        
        if role_id:
            role = db.session.get(Role, role_id)
            if role:
                user.roles = [role]
                
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update_user(user: User, data: dict, password: Optional[str] = None, role_id: Optional[int] = None,) -> User:
        if data.get("picture"): 
            user.picture = data["picture"]

        user.username = data["username"]
        user.email = data["email"]
        user.full_name = data["full_name"]
        user.phone_number = data["phone_number"]
        user.is_active = data.get("is_active", True)

        if password:
            user.set_password(password)

        if role_id:
            role = db.session.get(Role, role_id)
            if role:
                user.roles = [role]

        db.session.commit()
        return user

    @staticmethod
    def delete(user: User) -> None:
        db.session.delete(user)
        db.session.commit()
