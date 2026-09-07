import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from extensions import db
from app.models.user import User
from app.models.role import Role
from app.services.user_service import UserService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_user_role_names(user: User) -> list[str]:
    """Helper function to safely extract role names in lowercase."""
    role_names = []

    # Case 1: user.roles is a list of Role models or strings
    if hasattr(user, "roles") and user.roles:
        for r in user.roles:
            name = r.name if hasattr(r, "name") else str(r)
            if name:
                role_names.append(name.lower())

    # Case 2: user.role is a single Role model or string
    elif hasattr(user, "role") and user.role:
        r = user.role
        name = r.name if hasattr(r, "name") else str(r)
        if name:
            role_names.append(name.lower())

    return role_names


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash(
                    "Your account is inactive. Please contact administrator.",
                    "warning",
                )
                return redirect(url_for("auth.login"))

            login_user(user)
            flash("Logged in successfully.", "success")

            # Extract user roles safely
            user_roles = get_user_role_names(user)
            is_admin_flag = getattr(user, "is_admin", False)

            # Debug output in terminal to verify roles loaded for user
            print(
                f"[DEBUG LOGIN] User '{username}' logged in. Roles: {user_roles}, is_admin: {is_admin_flag}"
            )

            # Role-Based Login Redirects
            if is_admin_flag or "admin" in user_roles:
                return redirect(
                    url_for("users.index")
                )  # Admins go to User Management
            elif "dermatologist" in user_roles:
                return redirect(
                    url_for("diagnoses.dashboard")
                )  # Dermatologists go to Symptoms
            else:
                return redirect(
                    url_for("diagnoses.dashboard")
                )  # Standard Users go to Diseases Library

        flash("Invalid username or password", "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        full_name = request.form.get("full_name", "").strip()
        phone_number = request.form.get("phone_number", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        picture = request.files.get("picture")

        errors: list[str] = []

        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        if not full_name:
            errors.append("Full name is required.")
        if not phone_number:
            errors.append("Phone number is required.")
        if not password:
            errors.append("Password is required.")
        if password and password != confirm_password:
            errors.append("Passwords do not match.")

        if username and User.query.filter_by(username=username).first():
            errors.append("This username is already taken.")
        if email and User.query.filter_by(email=email).first():
            errors.append("This email is already registered.")
        if phone_number and User.query.filter_by(
            phone_number=phone_number
        ).first():
            errors.append("This phone number is already registered.")

        if errors:
            for msg in errors:
                flash(msg, "danger")
            return render_template(
                "auth/register.html",
                username=username,
                email=email,
                full_name=full_name,
                phone_number=phone_number,
            )

        # Profile Picture Upload Handling
        profile_picture = None
        if picture and picture.filename != "":
            filename = secure_filename(f"{username}_avatar.png")
            upload_folder = os.path.join("app", "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            upload_path = os.path.join(upload_folder, filename)
            picture.save(upload_path)
            profile_picture = filename

        # Fetch or auto-create default 'User' role if missing
        default_role = Role.query.filter_by(name="User").first()
        if not default_role:
            default_role = Role(
                name="User", description="Standard default user role"
            )
            db.session.add(default_role)
            db.session.commit()

        data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "phone_number": phone_number,
            "picture": profile_picture,
            "is_active": True,
        }

        # Create user via UserService
        new_user = UserService.create_user(
            data=data,
            password=password,
            role_id=default_role.id,
        )

        login_user(new_user)
        flash("Account created successfully. You are now logged in.", "success")

        # Redirect newly registered standard users straight to diagnosis screen
        return redirect(url_for("diagnoses.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))