from datetime import datetime
from extensions import db

class Fact(db.Model):
    __tablename__ = "facts"

    id = db.Column(db.Integer, primary_key=True)
    
    symptom = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Optional global default confidence (or remove this column if using dynamic weights exclusively)
    # confidence = db.Column(db.Numeric(5, 2)) 

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Updated Relationships
    rule_facts = db.relationship("RuleFact", back_populates="fact", cascade="all, delete-orphan")
    diagnose_facts = db.relationship("DiagnoseFact", back_populates="fact", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Fact {self.symptom}>"