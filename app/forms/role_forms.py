from collections import defaultdict
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Role, Permission
from extensions import db
from app.forms.multi_checkbox_field import MulticheckboxField

def _permission_choices():
    """Flat (id, label) list, used for field binding only."""
    return [
        (perm.id, f"{perm.code} - {perm.name}")
        for perm in db.session.scalars(
            db.select(Permission).order_by(Permission.code)
        )
    ]

def _permission_grouped_by_module():
    """
    Return permission grouped by module:
    {
        "Users": [Permission, ...],
        "Roles": [Permission, ...],
        ...
    }
    """
    perms = list(
        db.session.scalars(
            db.select(Permission).order_by(
                Permission.module, Permission.code
            )
        )
    )
    grouped = defaultdict(list)
    for perm in perms:
        module = perm.module or "General"
        grouped[module].append(perm)
    return dict(grouped)

class RoleCreateForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=80)],
        render_kw={"placeholder": "Role name"},
    )
    description = TextAreaField(
        "Description",
        render_kw={"placeholder": "Short description (optional)"},
    )
    
    permission_ids = MulticheckboxField(
        "Permissions",
        coerce=int,
        render_kw={"placeholder": "Permissions granted to this role"},
    )
    
    submit = SubmitField("Save")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission_ids.choices = _permission_choices()
        self.permissions_by_module = _permission_grouped_by_module()
        
    def validate_name(self, field):
        exists = db.session.scalar(
            db.select(Role).filter(Role.name == field.data)
        )
        if exists:
            raise ValidationError("This role name is already taken.")
        

class RoleEditForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=80)],
    )
    description = TextAreaField("Description")
    
    permission_ids = MulticheckboxField("Permissions",
        coerce=int,
    )
    
    submit = SubmitField("Update")
    
    def __init__(self, original_role: Role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_role = original_role
        self.permission_ids.choices = _permission_choices()
        self.permissions_by_module = _permission_grouped_by_module()
        
        if not self.is_submitted():
            self.permission_ids.data = [p.id for p in original_role.permissions]
            
    def validate_name(self, field):
        q = db.select(Role).filter(
            Role.name == field.data,
            Role.id != self.original_role.id,
        )
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("This role name iis already taken.")
        
class RoleConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")
    