# app/routes/diagnose_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.diagnose_form import DiagnoseForm
from app.services.diagnose_service import DiagnoseService, NoMatchingRuleError
from app.models.fact import Fact
from app.models.rule import Rule

diagnose_bp = Blueprint("diagnoses", __name__, url_prefix="/diagnoses")

@diagnose_bp.route("/dashboard")
@login_required
def dashboard():
    rules = Rule.query.all()
    return render_template("diagnoses/dashboard.html", rules=rules)

@diagnose_bp.route("/diagnose", methods=["GET", "POST"])
@login_required
def diagnose():
    form = DiagnoseForm()
    facts = Fact.query.all()

    if form.validate_on_submit():
        # Parse posted symptom severity inputs: symptom_SEVERITY_<fact_id>
        user_symptoms_dict = {}
        for key, value in request.form.items():
            if key.startswith("severity_") and float(value) > 0:
                fact_id = int(key.replace("severity_", ""))
                user_symptoms_dict[fact_id] = float(value)

        if not user_symptoms_dict:
            flash("Please select at least one active symptom with severity.", "warning")
            return redirect(url_for("diagnoses.diagnose"))

        try:
            diagnose_record = DiagnoseService.diagnose_user(
                user_id=current_user.id,
                user_symptoms_dict=user_symptoms_dict
            )

            flash("Diagnosis completed successfully!", "success")
            return redirect(url_for("diagnoses.diagnose_result", diagnose_id=diagnose_record.id))
        except NoMatchingRuleError:
            flash("No matching condition found for selected symptoms. Please consult a dermatologist.", "warning")
            return redirect(url_for("diagnoses.diagnose"))

    return render_template("diagnoses/_form.html", form=form, facts=facts)

@diagnose_bp.route("/result/<int:diagnose_id>")
@login_required
def diagnose_result(diagnose_id: int):
    diagnose = DiagnoseService.get_diagnose_by_id(diagnose_id)
    if not diagnose:
        flash("Diagnosis record not found.", "danger")
        return redirect(url_for("diagnoses.diagnose"))

    return render_template("diagnoses/_result.html", diagnose=diagnose)

@diagnose_bp.route("/history")
@login_required
def diagnose_history():
    diagnoses = DiagnoseService.get_diagnose_by_user(current_user.id)
    return render_template("diagnoses/_history.html", diagnoses=diagnoses)