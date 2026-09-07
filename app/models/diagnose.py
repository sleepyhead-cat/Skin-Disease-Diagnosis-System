from datetime import datetime
from extensions import db
from app.models.associations import diagnose_rules

class Diagnose(db.Model):
    __tablename__ = "diagnoses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Calculated Dynamic Certainty (e.g., 87.50 for 87.5%) capped at max 99.00%
    certainty = db.Column(db.Numeric(5, 2)) 

    diagnosed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    rules = db.relationship("Rule", secondary=diagnose_rules, back_populates="diagnoses")
    diagnose_facts = db.relationship("DiagnoseFact", back_populates="diagnose", cascade="all, delete-orphan")
    users = db.relationship("User", back_populates="diagnoses")

    def __repr__(self):
        return f"<Diagnose {self.id} certainty={self.certainty}>"