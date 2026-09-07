# app/models/associations.py
from extensions import db

user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)

role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True),
)

# --- EXPLICIT JUNCTION MODEL FOR RULE & FACT WEIGHTS ---
class RuleFact(db.Model):
    __tablename__ = "rule_facts"

    rule_id = db.Column(db.Integer, db.ForeignKey("rules.id"), primary_key=True)
    fact_id = db.Column(db.Integer, db.ForeignKey("facts.id"), primary_key=True)
    
    # Weight of this symptom (Fact) for this specific disease (Rule)
    # Default is 0.70 (70% weight), max encouraged is 0.90
    weight_factor = db.Column(db.Numeric(3, 2), default=0.70, nullable=False)

    rule = db.relationship("Rule", back_populates="rule_facts")
    fact = db.relationship("Fact", back_populates="rule_facts")

# --- USER DIAGNOSIS SYMPTOM SEVERITY ---
class DiagnoseFact(db.Model):
    __tablename__ = "diagnose_facts"

    diagnose_id = db.Column(db.Integer, db.ForeignKey("diagnoses.id"), primary_key=True)
    fact_id = db.Column(db.Integer, db.ForeignKey("facts.id"), primary_key=True)
    
    # Patient severity input for this diagnosis session (0.3=Mild, 0.6=Moderate, 0.9=Severe)
    severity = db.Column(db.Numeric(3, 2), default=0.60, nullable=False)

    diagnose = db.relationship("Diagnose", back_populates="diagnose_facts")
    fact = db.relationship("Fact", back_populates="diagnose_facts")

diagnose_rules = db.Table(
    "diagnose_rules",
    db.Column("diagnose_id", db.Integer, db.ForeignKey("diagnoses.id"), primary_key=True),
    db.Column("rule_id", db.Integer, db.ForeignKey("rules.id"), primary_key=True),
)

user_diagnoses = db.Table(
    "user_diagnoses",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("diagnose_id", db.Integer, db.ForeignKey("diagnoses.id"), primary_key=True),
)

rule_diagnoses = db.Table(
    "rule_diagnoses",
    db.Column("rule_id", db.Integer, db.ForeignKey("rules.id"), primary_key=True),
    db.Column("diagnose_id", db.Integer, db.ForeignKey("diagnoses.id"), primary_key=True),
)