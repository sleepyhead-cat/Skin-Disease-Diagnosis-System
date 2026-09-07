import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import BooleanField, StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional

from app.models import User
from app.models import Role
from extensions import db

#------Helpers------
def strong_password(form, field):
    """Require: min 8 chars, upper, lower, digit, special"""
    password = field.data or ""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    
    if not re.search(r"[0-9]", password):
        raise ValidationError("Password must contain at least one digit.")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", password):
        raise ValidationError("Password must contain at least one special character.")
    
def _role_choice():
    """Return list of (id, name) tuples for all roles, ordered by name."""
    return [
        (role.id, role.name)
        for role in db.session.scalars(
            db.select(Role).order_by(Role.name)
        )
    ]

#------Create form Validators(password required)------
class UserCreateForm(FlaskForm):
    picture = FileField(
        "Picture",
        validators=[FileAllowed(["jpg", "jpeg", "png", "gif"], "Image Only")]
    )
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={"placeholder": "Enter username"},
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={"placeholder": "email@example.com"},
    )
    full_name = StringField(
        "Full name",
        validators=[DataRequired(), Length(min=3 ,max=120)],
        render_kw={"placeholder": "Enter full name"},
    )
    phone_number = StringField(
        "Phone number",
        validators=[DataRequired(), Length(min=9 ,max=15)],
        render_kw={"placeholder": "xxx xxx xxx"},
    )
    is_active = BooleanField("Active", default=True)
    
    role_id = SelectField(
        "Role",
        coerce=int,
        validators=[DataRequired()],
        render_kw={"placeholder": "Select role"},
    )
    
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            strong_password,
            ],
        render_kw={"placeholder": "Strong password"},
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Password must match."),
        ],
        render_kw={"placeholder": "Confirm password"},
    )
    
    submit = SubmitField("Create")
    
    #------Server-side uniquenness checks------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_id.choices = _role_choice()
        
    def validate_username(self, field):
        exists = db.session.scalar(
            db.select(User).filter(User.username == field.data)
        )
        if exists:
            raise ValidationError("This username is already taken.")
        
    def validate_email(self, field):
        exists = db.session.scalar(
            db.select(User).filter(User.email == field.data)
        )
        if exists:
            raise ValidationError("This email is already registered.")
        
    def validate_phone_number(self, field):
        exists = db.session.scalar(
            db.select(User).filter(User.phone_number == field.data)
        )
        if exists:
            raise ValidationError("This phone number is already registered.")

#------Edit form(password optional)------
class UserEditForm(FlaskForm):
    picture = FileField(
        "Picture",
        validators=[FileAllowed(["jpg", "jpeg", "png", "gif"], "Image Only")]
    )
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=80)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)],
    )
    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=3 ,max=120)],
    )
    phone_number = StringField(
        "Phone Number",
        validators=[DataRequired(), Length(min=9, max=15)],
    )
    is_active = BooleanField("Active")
    
    role_id = SelectField(
        "Role", 
        coerce=int,
        validators=[DataRequired()],
    )
    
    # Optional password - only change if filled
    password = PasswordField(
        "New password (leave blank to keep current)",
        validators= [Optional(), strong_password], 
        render_kw={"placeholder": "New strong password (optional)"},
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators= [EqualTo("password", message="Password must match.")], 
    )
    
    submit = SubmitField("Update")
    
    def __init__(self, original_user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_user = original_user
        self.role_id.choices = _role_choice()
        
        if not self.is_submitted():
            if original_user.roles:
                self.role_id.data = original_user.roles[0].id
            else:
                self.role_id.data = None
        
    def validate_username(self, field):
        q = db.select(User).filter(User.username == field.data, User.id != self.original_user.id)
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This username is already taken.")
        
    def validate_email(self, field):
        q = db.select(User).filter(User.email == field.data, User.id != self.original_user.id)
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This email is already registered.")
    
    def validate_phone_number(self, field):
        q = db.select(User).filter(User.phone_number == field.data, User.id != self.original_user.id)
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This phone number is already registered.")
        
class UserConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")
        