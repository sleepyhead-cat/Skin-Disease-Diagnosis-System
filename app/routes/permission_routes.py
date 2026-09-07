from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.permission import Permission
from app.utils.decorators import has_permission
from extensions import db

permission_bp = Blueprint("permissions", __name__, url_prefix="/permissions")

@permission_bp.route("/")
@login_required
@has_permission("role.manage")
def index():
    permissions = Permission.query.order_by(Permission.module, Permission.code).all()
    return render_template("permissions/index.html", permissions=permissions)

@permission_bp.route("/create", methods=["POST"])
@login_required
@has_permission("role.manage")
def create():
    code = request.form.get("code", "").strip()
    name = request.form.get("name", "").strip()
    module = request.form.get("module", "General").strip()
    description = request.form.get("description", "").strip()

    if not code or not name:
        flash("Both Permission Code and Name are required.", "danger")
        return redirect(url_for("permissions.index"))

    if Permission.query.filter_by(code=code).first():
        flash(f"Permission code '{code}' already exists.", "danger")
        return redirect(url_for("permissions.index"))

    perm = Permission(code=code, name=name, module=module, description=description)
    db.session.add(perm)
    db.session.commit()

    flash(f"Permission '{perm.name}' ({perm.code}) created successfully!", "success")
    return redirect(url_for("permissions.index"))