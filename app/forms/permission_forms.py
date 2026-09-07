from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.permission import Permission
from extensions import db

MODULE_CHOICES = [
    ("Users", "Users"),
    ("Roles", "Roles"),
    ("Permissions", "Permissions"),
    ("System", "System"),
    ("Audit", "Audit"),
    ("General", "General"),
]

class PermissionCreateForm(FlaskForm):
    code = StringField(
        "Code",
        validators=[DataRequired(), Length(min=2, max=64)],
        render_kw={"placeholder": "e.g. user.view"},
    )
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=10)],
        render_kw={"placeholder": "Human-readable name"},
    )
    module = SelectField(
        "Module",
        choices=MODULE_CHOICES,
        default="General",
    )
    description = TextAreaField(
        "Description",
        render_kw={"placeholder": "What does this permission allow?"},
    )
    
    submit = SubmitField("Save")
    
    def validate_code(self, field):
        exists = db.session.scalar(
            db.select(Permission).filter(Permission.code == field.data)
        )
        if exists:
            raise ValidationError("This permission code is already in use.")
    
    def validate_name(self, field):
        exists = db.session.scalar(
            db.select(Permission).filter(Permission.name == field.data)
        )       
        if exists:
            raise ValidationError("This permission name is already in use.")
        
class PermissionEditForm(FlaskForm):
    code = StringField(
        "Code",
        validators=[DataRequired(), Length(min=2, max=64)],
    )
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=10)],
    )
    module = SelectField(
        "Module",
        choices=MODULE_CHOICES,
        default="General",
    )
    description = TextAreaField("Description")
    
    submit = SubmitField("Update")
    
    def __init__(self, original_permission: Permission, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_permission = original_permission
        if not self.is_submitted():
            self.module.data = original_permission.module
    
    def validate_code(self, field):
        q = db.select(Permission).filter(
            Permission.code == field.data,
            Permission.id != self.original_permission.id,
        )
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This permission code is already in use.")
    
    def validate_name(self, field):
        q = db.select(Permission).filter(
            Permission.name == field.data,
            Permission.id != self.original_permission.id,
        )
        exists = db.session.scalar(q)       
        if exists:
            raise ValidationError("This permission name is already in use.")
        
class PermissionConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")
        
    