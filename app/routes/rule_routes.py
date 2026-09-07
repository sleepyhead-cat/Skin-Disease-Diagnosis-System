import os
from werkzeug.utils import secure_filename

from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required
from app.forms.rule_forms import RuleCreateForm, RuleEditForm, RuleConfirmDeleteForm
from app.services.rule_service import RuleService
from app.models.rule import Rule

rule_bp = Blueprint("rules", __name__, url_prefix="/rules")

@rule_bp.route("/")
@login_required
def index():
    rules = RuleService.get_rule_all()
    return render_template("rules/index.html", rules=rules)

@rule_bp.route("/<int:rule_id>")
@login_required
def detail(rule_id: int):
    rule = RuleService.get_rule_by_id(rule_id)
    if rule is None:
        abort(404)
    return render_template("rules/detail.html", rule=rule)

@rule_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = RuleCreateForm()
    if form.validate_on_submit():
        picture = form.picture.data
        profile_rule = None

        if picture and hasattr(picture, "filename") and picture.filename:
            filename = secure_filename(f"{form.disease.data}_disease.png")
            upload_folder = os.path.join("app", "static", "diseasePic")
            os.makedirs(upload_folder, exist_ok=True)
            upload_path = os.path.join(upload_folder, filename)
            picture.save(upload_path)
            profile_rule = filename

        data = { 
            "picture": profile_rule,
            "disease": form.disease.data,
            "name": form.name.data,
            "urgency": form.urgency.data,
            "advice": form.advice.data,
            "description": form.description.data,
            "is_active": form.is_active.data,
        }

        fact_ids = form.fact_ids.data or []
        
        # Build dictionary mapping fact_id -> MB weight factor from form input
        fact_weights = {}
        for fid in fact_ids:
            weight_val = request.form.get(f"weight_{fid}", 0.70)
            fact_weights[int(fid)] = float(weight_val)

        rule = RuleService.create_rule(data, fact_weights)   
        flash(f"Rule '{rule.name}' created successfully!", "success")
        return redirect(url_for("rules.index"))

    return render_template("rules/create.html", form=form, existing_weights={})

@rule_bp.route("/edit/<int:rule_id>", methods=["GET", "POST"])
@login_required
def edit(rule_id):
    rule = RuleService.get_rule_by_id(rule_id)
    if rule is None:
        abort(404)

    form = RuleEditForm(original_rule=rule, obj=rule)
    
    if form.validate_on_submit():
        picture = form.picture.data
        profile_rule = rule.picture  # keep old picture if no new one

        if picture and hasattr(picture, "filename") and picture.filename:
            filename = secure_filename(f"{form.disease.data}_disease.png")
            upload_folder = os.path.join("app", "static", "diseasePic")
            os.makedirs(upload_folder, exist_ok=True)
            upload_path = os.path.join(upload_folder, filename)
            picture.save(upload_path)
            profile_rule = filename
        
        data = {
            "picture": profile_rule,
            "disease": form.disease.data,
            "name": form.name.data,
            "urgency": form.urgency.data,
            "advice": form.advice.data,
            "description": form.description.data,
            "is_active": form.is_active.data,
        }
        
        fact_ids = form.fact_ids.data or []
        
        # Build dictionary mapping fact_id -> MB weight factor from form input
        fact_weights = {}
        for fid in fact_ids:
            weight_val = request.form.get(f"weight_{fid}", 0.70)
            fact_weights[int(fid)] = float(weight_val)
        
        RuleService.update_rule(rule, data, fact_weights)
        flash(f"Disease '{rule.disease}' was updated successfully!", "success")
        return redirect(url_for("rules.index"))

    # Map existing weights for pre-filling input fields in rules/_form.html
    existing_weights = {rf.fact_id: rf.weight_factor for rf in rule.rule_facts}

    return render_template("rules/edit.html", form=form, rule=rule, existing_weights=existing_weights)

@rule_bp.route("/<int:rule_id>/delete", methods=["GET"])
@login_required
def delete_confirm(rule_id: int):
    rule = RuleService.get_rule_by_id(rule_id)
    if rule is None:
        abort(404)
        
    form = RuleConfirmDeleteForm()
    return render_template("rules/delete_confirm.html", rule=rule, form=form)

@rule_bp.route("/delete/<int:rule_id>", methods=["POST"])
@login_required
def delete(rule_id: int):
    rule = RuleService.get_rule_by_id(rule_id)
    if not rule:
        abort(404)
    
    RuleService.delete_rule(rule)
    flash("Disease was deleted successfully.", "success")
    return redirect(url_for("rules.index"))