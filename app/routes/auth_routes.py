import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from sqlalchemy import or_

from extensions import db
from app.models.user import User
from app.models.role import Role
from app.services.user_service import UserService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_user_role_names(user: User) -> list[str]:
    """Helper function to safely extract role names in lowercase."""
    role_names = []

    print(f"[DEBUG ROLE CHECK] Inspecting roles for user ID: {getattr(user, 'id', None)}")

    if hasattr(user, "roles") and user.roles:
        print(f"[DEBUG ROLE CHECK] Found 'roles' attribute: {user.roles}")
        for r in user.roles:
            name = r.name if hasattr(r, "name") else str(r)
            if name:
                role_names.append(name.lower())
    elif hasattr(user, "role") and user.role:
        print(f"[DEBUG ROLE CHECK] Found 'role' attribute: {user.role}")
        r = user.role
        name = r.name if hasattr(r, "name") else str(r)
        if name:
            role_names.append(name.lower())
    else:
        print("[DEBUG ROLE CHECK] No roles or role attribute found on user object!")

    return role_names


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_input = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        print("\n" + "=" * 50)
        print(f"[DEBUG LOGIN] Attempting login for input: '{login_input}'")

        # 1. Lookup user by Username OR Email
        user = User.query.filter(
            or_(User.username == login_input, User.email == login_input)
        ).first()

        if not user:
            print(f"[DEBUG LOGIN] FAILED: User '{login_input}' not found in database.")
            flash("Invalid username/email or password", "danger")
            return redirect(url_for("auth.login"))

        print(f"[DEBUG LOGIN] Found User ID: {user.id}, Email: {user.email}, Is Active: {user.is_active}")

        # 2. Check password
        password_valid = user.check_password(password)
        print(f"[DEBUG LOGIN] Password check result: {password_valid}")

        if not password_valid:
            print(f"[DEBUG LOGIN] FAILED: Invalid password provided for '{login_input}'.")
            flash("Invalid username/email or password", "danger")
            return redirect(url_for("auth.login"))

        # 3. Check account status
        if not user.is_active:
            print(f"[DEBUG LOGIN] FAILED: Account for '{login_input}' is INACTIVE.")
            flash(
                "Your account is inactive. Please contact administrator.",
                "warning",
            )
            return redirect(url_for("auth.login"))

        # 4. Create Flask-Login session
        login_success = login_user(user)
        print(f"[DEBUG LOGIN] Flask-Login login_user() result: {login_success}")

        # 5. Extract Roles & Flags
        user_roles = get_user_role_names(user)
        is_admin_flag = getattr(user, "is_admin", False)

        print(f"[DEBUG LOGIN] Extracted Roles: {user_roles}")
        print(f"[DEBUG LOGIN] Extracted is_admin flag: {is_admin_flag}")

        # 6. Determine Redirect Target
        if is_admin_flag or "admin" in user_roles:
            target_route = "users.index"
        elif "doctor" in user_roles or "dermatologist" in user_roles:
            target_route = "diagnoses.dashboard"
        else:
            target_route = "diagnoses.dashboard"

        print(f"[DEBUG LOGIN] Target route calculated: '{target_route}'")

        try:
            target_url = url_for(target_route)
            print(f"[DEBUG LOGIN] Generated target URL: '{target_url}'")
            print("=" * 50 + "\n")
            flash("Logged in successfully.", "success")
            return redirect(target_url)
        except Exception as e:
            print(f"[DEBUG LOGIN ERROR] Failed to generate URL for route '{target_route}': {e}")
            print("=" * 50 + "\n")
            flash(f"Redirect error: Route '{target_route}' not found.", "danger")
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

        print("\n" + "=" * 50)
        print(f"[DEBUG REGISTER] Registration attempt for username: '{username}', email: '{email}'")

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
            print(f"[DEBUG REGISTER] Validation failed with errors: {errors}")
            for msg in errors:
                flash(msg, "danger")
            return render_template(
                "auth/register.html",
                username=username,
                email=email,
                full_name=full_name,
                phone_number=phone_number,
            )

        profile_picture = None
        if picture and picture.filename != "":
            filename = secure_filename(f"{username}_avatar.png")
            upload_folder = os.path.join("app", "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            upload_path = os.path.join(upload_folder, filename)
            picture.save(upload_path)
            profile_picture = filename
            print(f"[DEBUG REGISTER] Saved profile picture to: {upload_path}")

        default_role = Role.query.filter_by(name="User").first()
        if not default_role:
            print("[DEBUG REGISTER] Default role 'User' not found. Creating it now...")
            default_role = Role(
                name="User", description="Standard default user role"
            )
            db.session.add(default_role)
            db.session.commit()

        print(f"[DEBUG REGISTER] Using default role ID: {default_role.id} ({default_role.name})")

        data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "phone_number": phone_number,
            "picture": profile_picture,
            "is_active": True,
        }

        new_user = UserService.create_user(
            data=data,
            password=password,
            role_id=default_role.id,
        )

        print(f"[DEBUG REGISTER] Created new User with ID: {new_user.id}")

        login_user(new_user)
        print(f"[DEBUG REGISTER] Logged in user ID: {new_user.id}")
        print("=" * 50 + "\n")

        flash("Account created successfully. You are now logged in.", "success")
        return redirect(url_for("diagnoses.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    print("[DEBUG LOGOUT] Logging out current user...")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))