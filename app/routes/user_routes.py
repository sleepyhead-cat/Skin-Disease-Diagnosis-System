import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

from app.forms.user_forms import UserCreateForm, UserEditForm, UserConfirmDeleteForm
from app.services.user_service import UserService
from app.utils.decorators import has_permission

user_bp = Blueprint("users", __name__, url_prefix="/users")

@user_bp.route("/")
@login_required
@has_permission("user.view")
def index():
    users = UserService.get_user_all()
    return render_template("users/index.html", users=users)
    
@user_bp.route("/<int:user_id>")
@login_required
@has_permission("user.view")
def detail(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if user is None:
        abort(404)
    return render_template("users/detail.html", user=user)

@user_bp.route("/create", methods=["GET", "POST"])
@login_required
@has_permission("user.manage")
def create():
    form = UserCreateForm()
    if form.validate_on_submit():
        picture = form.picture.data
        profile_picture = None
        if picture and hasattr(picture, "filename") and picture.filename:
            filename = secure_filename(f"{form.username.data}_avatar.png")
            upload_folder = os.path.join("app", "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            upload_path = os.path.join(upload_folder, filename)
            picture.save(upload_path)
            profile_picture = filename
            
        data = {
            "picture": profile_picture,
            "username": form.username.data,
            "email": form.email.data,
            "full_name": form.full_name.data,
            "phone_number": form.phone_number.data,
            "is_active": form.is_active.data,
        }
        password = form.password.data
        role_id = form.role_id.data or None
        
        user = UserService.create_user(data, password, role_id)
        flash(f"User '{user.username}' was created successfully.", "success")
        return redirect(url_for("users.index"))
    
    return render_template("users/create.html", form=form)

@user_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@has_permission("user.manage")
def edit(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if user is None:
        abort(404)
        
    form = UserEditForm(original_user=user, obj=user)
    
    if form.validate_on_submit():
        # Prevent self-deactivation by admin
        if user.id == current_user.id and not form.is_active.data:
            flash("You cannot deactivate your own account.", "warning")
            form.is_active.data = True

        picture = form.picture.data
        profile_picture = user.picture  # Keep existing picture if no new upload

        if picture and hasattr(picture, "filename") and picture.filename:
            filename = secure_filename(f"{form.username.data}_avatar.png")
            upload_folder = os.path.join("app", "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            upload_path = os.path.join(upload_folder, filename)
            picture.save(upload_path)
            profile_picture = filename
            
        data = {
            "picture": profile_picture,
            "username": form.username.data,
            "email": form.email.data,
            "full_name": form.full_name.data,
            "phone_number": form.phone_number.data,
            "is_active": form.is_active.data,
        }
        password = form.password.data or None
        role_id = form.role_id.data or None
        
        UserService.update_user(user, data, password, role_id)
        flash(f"User '{user.username}' was updated successfully.", "success")
        return redirect(url_for("users.detail", user_id=user_id))
    
    return render_template("users/edit.html", form=form, user=user)

@user_bp.route("/<int:user_id>/delete", methods=["GET"])
@login_required
@has_permission("user.manage")
def delete_confirm(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if user is None:
        abort(404)
        
    form = UserConfirmDeleteForm()
    return render_template("users/delete_confirm.html", user=user, form=form)

@user_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@has_permission("user.manage")
def delete(user_id: int):
    user = UserService.get_user_by_id(user_id)
    if user is None:
        abort(404)

    # Protect against deleting oneself
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("users.index"))
        
    UserService.delete(user)
    flash("User was deleted successfully.", "success")
    return redirect(url_for("users.index"))