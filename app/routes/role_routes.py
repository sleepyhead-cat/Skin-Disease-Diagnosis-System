from collections import defaultdict
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required

from app.models.role import Role
from app.models.permission import Permission

from app.forms.role_forms import RoleEditForm

from app.utils.decorators import has_permission
from extensions import db

role_bp = Blueprint("roles", __name__, url_prefix="/roles")

@role_bp.route("/")
@login_required
@has_permission("role.manage")
def index():
    roles = Role.query.all()
    return render_template("roles/index.html", roles=roles)

@role_bp.route("/create", methods=["GET", "POST"])
@login_required
@has_permission("role.manage")
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        selected_perm_ids = request.form.getlist("permission_ids")

        if not name:
            flash("Role name is required.", "danger")
            return redirect(url_for("roles.create"))

        if Role.query.filter_by(name=name).first():
            flash(f"Role '{name}' already exists.", "danger")
            return redirect(url_for("roles.create"))

        role = Role(name=name, description=description)

        if selected_perm_ids:
            perms = Permission.query.filter(Permission.id.in_(selected_perm_ids)).all()
            role.permissions.extend(perms)

        db.session.add(role)
        db.session.commit()
        flash(f"Role '{role.name}' created successfully!", "success")
        return redirect(url_for("roles.index"))

    # Group permissions by module for easier selection in UI
    all_permissions = Permission.query.order_by(Permission.module, Permission.name).all()
    grouped_permissions = defaultdict(list)
    for perm in all_permissions:
        module_name = perm.module if perm.module else "General"
        grouped_permissions[module_name].append(perm)

    return render_template("roles/create.html", grouped_permissions=grouped_permissions)

@role_bp.route("/<int:role_id>/edit", methods=["GET", "POST"])
@login_required
@has_permission("role.manage")
def edit(role_id: int):
    role = Role.query.get_or_404(role_id)
    form = RoleEditForm(original_role=role, obj=role)

    if form.validate_on_submit():
        role.name = form.name.data.strip()
        role.description = form.description.data.strip() if form.description.data else ""

        selected_perm_ids = form.permission_ids.data or []
        if selected_perm_ids:
            perms = Permission.query.filter(Permission.id.in_(selected_perm_ids)).all()
            role.permissions = perms
        else:
            role.permissions = []

        db.session.commit()
        flash(f"Role '{role.name}' updated successfully!", "success")
        return redirect(url_for("roles.index"))

    all_permissions = Permission.query.order_by(Permission.module, Permission.name).all()
    grouped_permissions = defaultdict(list)
    for perm in all_permissions:
        module_name = perm.module if perm.module else "General"
        grouped_permissions[module_name].append(perm)

    return render_template(
        "roles/edit.html", 
        form=form, 
        role=role, 
        grouped_permissions=grouped_permissions
    )

@role_bp.route("/<int:role_id>/delete", methods=["POST"])
@login_required
@has_permission("role.manage")
def delete(role_id: int):
    role = Role.query.get_or_404(role_id)

    # Protect essential system roles from accidental deletion
    if role.name in ["Admin", "User"]:
        flash(f"System role '{role.name}' cannot be deleted.", "warning")
        return redirect(url_for("roles.index"))

    db.session.delete(role)
    db.session.commit()
    flash(f"Role '{role.name}' deleted successfully.", "success")
    return redirect(url_for("roles.index"))