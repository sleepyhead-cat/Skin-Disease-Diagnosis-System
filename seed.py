# seed.py
import json
import os
from app import create_app
from extensions import db
from app.models import User, Role, Permission, Fact, Rule, RuleFact

app = create_app()

def run_seed():
    with app.app_context():
        # Ensure database tables exist
        db.create_all()

        print("1. Syncing Permissions...")
        permissions_data = [
            # User Management
            {"code": "user.view", "name": "View Users", "module": "User Management", "description": "View user accounts list"},
            {"code": "user.manage", "name": "Manage Users", "module": "User Management", "description": "Create, edit, and delete users"},
            # Roles & Permissions
            {"code": "role.view", "name": "View Roles", "module": "Role Management", "description": "View roles and assigned permissions"},
            {"code": "role.manage", "name": "Manage Roles", "module": "Role Management", "description": "Create, edit, assign permissions to roles"},
            {"code": "permission.view", "name": "View Permissions", "module": "Role Management", "description": "View system permissions registry"},
            {"code": "permission.manage", "name": "Manage Permissions", "module": "Role Management", "description": "Add or modify system permissions"},
            # Knowledge Base (Facts & Rules)
            {"code": "fact.manage", "name": "Manage Facts", "module": "Disease Management", "description": "Create, edit, delete symptoms/facts"},
            {"code": "rule.manage", "name": "Manage Rules", "module": "Disease Management", "description": "Create, edit, delete disease rules and weights"},
            # Diagnosis
            {"code": "diagnose.run", "name": "Run Diagnosis", "module": "Diagnosis", "description": "Access and execute skin disease diagnosis"},
        ]

        perm_map = {}
        for item in permissions_data:
            perm = Permission.query.filter_by(code=item["code"]).first()
            if not perm:
                perm = Permission(
                    code=item["code"],
                    name=item["name"],
                    module=item["module"],
                    description=item.get("description")
                )
                db.session.add(perm)
            else:
                perm.name = item["name"]
                perm.module = item["module"]
                perm.description = item.get("description")
            db.session.commit()
            perm_map[perm.code] = perm
        print(f"   ✓ {len(perm_map)} Permissions registered.")

        print("\n2. Syncing Roles & Assigning Permissions...")
        # Admin Role
        admin_role = Role.query.filter_by(name="Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="System Administrator with full access")
            db.session.add(admin_role)
            db.session.commit()
        # Admin gets all permissions
        admin_role.permissions = list(perm_map.values())
        db.session.commit()

        # Regular User Role
        user_role = Role.query.filter_by(name="User").first()
        if not user_role:
            user_role = Role(name="User", description="Standard registered user")
            db.session.add(user_role)
            db.session.commit()
        # Standard user gets diagnosis access
        if "diagnose.run" in perm_map:
            user_role.permissions = [perm_map["diagnose.run"]]
            db.session.commit()

        print("   ✓ Roles & permission associations updated.")

        print("\n3. Syncing Initial Users...")
        # Admin Account
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="System Admin",
                phone_number="012345678",
                is_active=True
            )
            admin_user.set_password("admin123")
            if admin_role not in admin_user.roles:
                admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
            print("   ✓ Admin user ready (admin / admin123)")
        else:
            if admin_role not in admin_user.roles:
                admin_user.roles.append(admin_role)
                db.session.commit()
            print("   ✓ Admin user already exists.")

        # Regular Test User
        test_user = User.query.filter_by(username="user").first()
        if not test_user:
            test_user = User(
                username="user",
                email="user@example.com",
                full_name="Standard User",
                phone_number="0987654321",
                is_active=True
            )
            test_user.set_password("user123")
            test_user.roles.append(user_role)
            db.session.add(test_user)
            db.session.commit()
            print("   ✓ Standard user ready (user / user123)")
        else:
            print("   ✓ Standard user already exists.")

        # Load JSON Knowledge Base data
        json_path = os.path.join(app.root_path, "..", "data", "seed_data.json")
        if not os.path.exists(json_path):
            print(f"   ✗ JSON seed file not found at: {json_path}")
            return

        with open(json_path, "r") as f:
            seed_data = json.load(f)

        print("\n4. Syncing Symptoms (Facts)...")
        fact_map = {}
        for item in seed_data.get("symptoms", []):
            fact = Fact.query.filter_by(symptom=item["symptom"]).first()
            if not fact:
                fact = Fact(symptom=item["symptom"], description=item.get("description"))
                db.session.add(fact)
            else:
                fact.description = item.get("description")
            db.session.commit()
            fact_map[fact.symptom] = fact
        print(f"   ✓ {len(fact_map)} Symptoms synced.")

        print("\n5. Syncing Disease Rules & Certainty Weights...")
        for item in seed_data.get("diseases", []):
            rule = Rule.query.filter_by(disease=item["disease"]).first()
            if not rule:
                rule = Rule(
                    disease=item["disease"],
                    name=item.get("name"),
                    urgency=item.get("urgency", False),
                    advice=item.get("advice"),
                    description=item.get("description"),
                    is_active=True
                )
                db.session.add(rule)
                db.session.commit()
            else:
                rule.name = item.get("name")
                rule.urgency = item.get("urgency", False)
                rule.advice = item.get("advice")
                rule.description = item.get("description")
                db.session.commit()

            # Sync Rule-Symptom Weights (RuleFact)
            for symptom_name, weight in item.get("weights", {}).items():
                if symptom_name in fact_map:
                    fact_obj = fact_map[symptom_name]
                    rf = RuleFact.query.filter_by(rule_id=rule.id, fact_id=fact_obj.id).first()
                    if not rf:
                        rf = RuleFact(rule_id=rule.id, fact_id=fact_obj.id, weight_factor=weight)
                        db.session.add(rf)
                    else:
                        rf.weight_factor = weight
            db.session.commit()

        print("   ✓ Disease rules and weight factors synced.")
        print("\n==========================================")
        print("SEED COMPLETE & READY FOR TESTING!")
        print("==========================================")

if __name__ == "__main__":
    run_seed()