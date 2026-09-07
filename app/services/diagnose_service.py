# app/services/diagnose_service.py
from extensions import db
from app.models import Rule, Diagnose, DiagnoseFact

class NoMatchingRuleError(Exception):
    """Raised when selected symptoms do not match any disease rule."""
    pass

class DiagnoseService:
    
    @staticmethod
    def diagnose_user(user_id: int, user_symptoms_dict: dict[int, float]) -> Diagnose:
        """
        user_symptoms_dict: { fact_id: severity_level (e.g., 0.3, 0.6, 0.9) }
        Filter out 0.0 severities (Absent symptoms).
        """
        # Clean user_symptoms_dict to exclude 0.0 (Absent) severities
        active_symptoms = {fid: sev for fid, sev in user_symptoms_dict.items() if sev > 0.0}

        if not active_symptoms:
            raise NoMatchingRuleError("No symptoms provided or all set to Absent.")

        # Query active rules
        rules = Rule.query.filter_by(is_active=True).all()
        evaluated_results = []

        for rule in rules:
            cf_combined = 0.0
            
            for rf in rule.rule_facts:
                if rf.fact_id in active_symptoms:
                    weight = float(rf.weight_factor)          # MB (Symptom weight for disease)
                    severity = active_symptoms[rf.fact_id]   # User Severity Input
                    
                    # Single symptom contribution
                    cf_i = weight * severity
                    
                    # Incremental CF combination formula
                    cf_combined = cf_combined + (cf_i * (1.0 - cf_combined))

            if cf_combined > 0:
                # Convert to percentage and cap at maximum 99.00%
                final_cf = min(round(cf_combined * 100, 2), 99.00)
                evaluated_results.append((rule, final_cf))

        if not evaluated_results:
            raise NoMatchingRuleError("No matching disease found for symptoms.")

        # Sort by highest certainty score
        evaluated_results.sort(key=lambda x: x[1], reverse=True)
        top_rule, top_certainty = evaluated_results[0]

        # Save Diagnosis session
        diagnose = Diagnose(
            user_id=user_id,
            certainty=top_certainty
        )
        
        # KEY FIX: Append top_rule directly to the relationship list
        diagnose.rules.append(top_rule)
        
        db.session.add(diagnose)

        # Save individual symptom severity choices (including present symptoms)
        for fact_id, severity in active_symptoms.items():
            diag_fact = DiagnoseFact(
                diagnose=diagnose,
                fact_id=fact_id,
                severity=severity
            )
            db.session.add(diag_fact)

        db.session.commit()
        return diagnose

    @staticmethod
    def get_diagnose_by_id(diagnose_id: int) -> Diagnose:
        return Diagnose.query.get(diagnose_id)

    @staticmethod
    def get_diagnose_by_user(user_id: int):
        return Diagnose.query.filter_by(user_id=user_id).order_by(Diagnose.diagnosed_at.desc()).all()