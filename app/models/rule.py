from datetime import datetime
from extensions import db
from app.models.associations import rule_diagnoses

class Rule(db.Model):
    __tablename__ = "rules"

    id = db.Column(db.Integer, primary_key=True)
    disease = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120))
    urgency = db.Column(db.Boolean, default=False, nullable=False)
    advice = db.Column(db.String(255))
    picture = db.Column(db.String(255))
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Updated Relationship to RuleFact explicit model
    rule_facts = db.relationship("RuleFact", back_populates="rule", cascade="all, delete-orphan")
    diagnoses = db.relationship("Diagnose", secondary=rule_diagnoses, back_populates="rules")

    def __repr__(self):
        return f"<Rule {self.disease}>"