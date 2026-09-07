from typing import List, Optional
from app.models.fact import Fact
from extensions import db

class FactService:
    @staticmethod
    def get_fact_all() -> List[Fact]:
        return Fact.query.order_by(Fact.symptom.asc()).all()
    
    @staticmethod
    def get_fact_by_id(fact_id: int) -> Optional[Fact]:
        return Fact.query.get(fact_id)
    
    @staticmethod
    def create_fact(data: dict) -> Fact:
        f = Fact(
            symptom=data["symptom"],
            description=data.get("description") or "",
        )
        db.session.add(f)
        db.session.commit()
        return f
    
    @staticmethod
    def update_fact(fact: Fact, data: dict) -> Fact:
        fact.symptom = data["symptom"]
        fact.description = data.get("description") or ""
        
        db.session.commit()
        return fact
    
    @staticmethod
    def delete_fact(fact: Fact) -> None:
        db.session.delete(fact)
        db.session.commit()