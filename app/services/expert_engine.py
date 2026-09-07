from app.models import Rule, RuleFact
from extensions import db
from app.models import Diagnose, DiagnoseFact, rule_diagnoses

def evaluate_diagnosis(user_symptoms_dict):
    """
    Evaluates diagnosis using Certainty Factor (CF) Theory.
    
    :param user_symptoms_dict: Dictionary mapping fact_id (int) -> severity (float/Decimal, e.g., 0.3, 0.6, 0.9)
    :return: Sorted list of evaluation results for active diseases
    """
    results = []
    
    # Query all active disease rules and preload their rule_facts
    active_rules = Rule.query.filter_by(is_active=True).all()
    
    for rule in active_rules:
        cf_combined = 0.0
        matched_facts = []
        
        # Iterate over rule-symptom weights configured by experts
        for rf in rule.rule_facts:
            if rf.fact_id in user_symptoms_dict:
                # Convert Decimals/Floats cleanly
                weight = float(rf.weight_factor)          # MB (Measure of Belief for disease)
                severity = float(user_symptoms_dict[rf.fact_id]) # Si (User Severity input)
                
                # Single symptom certainty factor contribution: CF_i = MB * S
                cf_i = weight * severity
                
                # Combine using Certainty Factor formula: CF_new = CF_old + CF_i * (1 - CF_old)
                cf_combined = cf_combined + (cf_i * (1.0 - cf_combined))
                
                matched_facts.append({
                    "fact_id": rf.fact_id,
                    "symptom_name": rf.fact.symptom,
                    "weight": weight,
                    "severity": severity,
                    "contribution": round(cf_i * 100, 1)
                })
        
        if cf_combined > 0:
            # Convert to percentage and apply medical safety cap (Maximum 99.0%)
            final_cf_percentage = min(round(cf_combined * 100, 2), 99.00)
            
            results.append({
                "rule_id": rule.id,
                "disease_name": rule.disease,
                "urgency": rule.urgency,
                "advice": rule.advice,
                "picture": rule.picture,
                "certainty": final_cf_percentage,
                "matched_facts": matched_facts
            })
            
    # Sort results with the highest certainty factor first
    results.sort(key=lambda x: x["certainty"], reverse=True)
    return results

def save_diagnosis_result(user_id, top_rule_id, calculated_certainty, user_symptoms_dict):
    """
    Persists diagnosis session, linked rule, and user severity inputs to the database.
    """
    new_diagnose = Diagnose(
        user_id=user_id,
        certainty=calculated_certainty
    )
    db.session.add(new_diagnose)
    db.session.flush() # Flushes to generate new_diagnose.id
    
    # Associate the top diagnosed disease rule
    if top_rule_id:
        db.session.execute(
            rule_diagnoses.insert().values(
                rule_id=top_rule_id,
                diagnose_id=new_diagnose.id
            )
        )
    
    # Record individual patient symptom severity ratings
    for fact_id, severity in user_symptoms_dict.items():
        diag_fact = DiagnoseFact(
            diagnose_id=new_diagnose.id,
            fact_id=fact_id,
            severity=severity
        )
        db.session.add(diag_fact)
        
    db.session.commit()
    return new_diagnose