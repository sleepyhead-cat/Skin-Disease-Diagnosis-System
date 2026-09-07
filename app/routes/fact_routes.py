from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required
from app.forms.fact_forms import FactCreateForm, FactEditForm, FactConfirmDeleteForm
from app.services.fact_service import FactService
from app.models.fact import Fact

fact_bp = Blueprint("facts", __name__, url_prefix="/facts")

@fact_bp.route("/")
@login_required
def index():
    facts = FactService.get_fact_all()
    return render_template("facts/index.html", facts=facts)

@fact_bp.route("/<int:fact_id>")
@login_required
def detail(fact_id: int):
    fact = FactService.get_fact_by_id(fact_id)
    if fact is None:
        abort(404)
    return render_template("facts/detail.html", fact=fact)

@fact_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = FactCreateForm()
    if form.validate_on_submit():
        data = {
            "symptom": form.symptom.data,
            "description": form.description.data,
        }
        f = FactService.create_fact(data)
        flash(f"Symptom '{f.symptom}' was created successfully!", "success")
        return redirect(url_for("facts.index"))
    return render_template("facts/create.html", form=form)

@fact_bp.route("/<int:fact_id>/edit", methods=["GET", "POST"])
@login_required
def edit(fact_id):
    fact = FactService.get_fact_by_id(fact_id)
    if not fact:
        flash("Symptom not found.", "danger")
        return redirect(url_for("facts.index"))

    # Explicitly bind request.form during POST submissions
    if request.method == "POST":
        form = FactEditForm(request.form, original_fact=fact)
    else:
        form = FactEditForm(obj=fact, original_fact=fact)

    if form.validate_on_submit():
        data = {
            "symptom": form.symptom.data,
            "description": form.description.data,
        }
        FactService.update_fact(fact, data)
        flash("Symptom updated successfully!", "success")
        return redirect(url_for("facts.index"))

    # Terminal debug print to immediately identify silent validation failures
    if request.method == "POST":
        print("\n=== WTFORMS VALIDATION ERRORS ===")
        print(form.errors)
        print("=================================\n")

    return render_template("facts/edit.html", form=form, fact=fact)

@fact_bp.route("/delete/<int:fact_id>", methods=["GET"])
@login_required
def delete_confirm(fact_id: int):
    fact = FactService.get_fact_by_id(fact_id)
    if fact is None:
        abort(404)
    
    form = FactConfirmDeleteForm()
    return render_template("facts/delete_confirm.html", fact=fact, form=form)

@fact_bp.route("/<int:fact_id>/delete", methods=["POST"])
@login_required
def delete(fact_id: int):  
    fact = FactService.get_fact_by_id(fact_id)
    if fact is None:
        abort(404)
    
    FactService.delete_fact(fact)
    flash("Symptom was deleted successfully.", "success")
    return redirect(url_for("facts.index"))