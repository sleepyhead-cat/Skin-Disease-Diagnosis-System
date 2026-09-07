# app/services/rule_service.py
from extensions import db
from app.models import Rule, RuleFact

class RuleService:

    @staticmethod
    def get_rule_all():
        return Rule.query.all()

    @staticmethod
    def get_rule_by_id(rule_id: int):
        return Rule.query.get(rule_id)

    @staticmethod
    def create_rule(data: dict, fact_weights: dict[int, float]):
        rule = Rule(**data)
        db.session.add(rule)
        db.session.flush()

        if fact_weights:
            for fact_id, weight in fact_weights.items():
                rf = RuleFact(
                    rule_id=rule.id,
                    fact_id=fact_id,
                    weight_factor=weight
                )
                db.session.add(rf)

        db.session.commit()
        return rule

    @staticmethod
    def update_rule(rule: Rule, data: dict, fact_weights: dict[int, float]):
        for key, value in data.items():
            setattr(rule, key, value)

        # Clear previous symptom weight relationships
        RuleFact.query.filter_by(rule_id=rule.id).delete()

        # Re-assign new symptom weights
        if fact_weights:
            for fact_id, weight in fact_weights.items():
                rf = RuleFact(
                    rule_id=rule.id,
                    fact_id=fact_id,
                    weight_factor=weight
                )
                db.session.add(rf)

        db.session.commit()
        return rule

    @staticmethod
    def delete_rule(rule: Rule):
        RuleFact.query.filter_by(rule_id=rule.id).delete()
        db.session.delete(rule)
        db.session.commit()