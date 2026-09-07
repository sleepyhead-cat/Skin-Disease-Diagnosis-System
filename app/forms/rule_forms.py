from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, DecimalField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
from app.models import Rule, Fact
from extensions import db
from app.forms.multi_checkbox_field import MulticheckboxField

def _fact_choices():
    """Flat (id, label) list, used for field binding only."""
    return [
        (f.id, f.symptom)
        for f in db.session.scalars(
            db.select(Fact).order_by(Fact.symptom)
        )
    ]

class RuleCreateForm(FlaskForm):
    disease = StringField("Disease",
        validators=[DataRequired(), Length(min=2, max=80)],
        render_kw={"placeholder": "Disease"})
    name = StringField("Name",
        validators=[DataRequired(), Length(min=2, max=80)],
        render_kw={"placeholder": "Disease Name"})
    urgency = BooleanField("Urgent", default=False)
    advice = StringField("Advice",
        validators=[DataRequired(), Length(min=2, max=255)],
        render_kw={"placeholder": "Disease treatment."})
    picture = FileField("Picture",
        validators=[FileAllowed(["jpg", "jpeg", "png", "gif"], "Image Only")])
    is_active = BooleanField("Active", default=True)
    description = TextAreaField("Description",
        render_kw={"placeholder": "Short description (optional)"})
    fact_ids = MulticheckboxField("Facts", coerce=int,
        render_kw={"placeholder": "Symptoms related to this Disease."})
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fact_ids.choices = _fact_choices()

    def validate_disease(self, field):
        exists = db.session.scalar(
            db.select(Rule).filter(Rule.disease == field.data)
        )
        if exists:
            raise ValidationError("A disease with this name already exists.")

class RuleEditForm(FlaskForm):
    disease = StringField("Disease",
        validators=[DataRequired(), Length(min=2, max=80)])
    name = StringField("Name",
        validators=[DataRequired(), Length(min=2, max=80)])
    urgency = BooleanField("Urgent", default=False)
    advice = StringField("Advice",
        validators=[DataRequired(), Length(min=2, max=255)])
    picture = FileField("Picture",
        validators=[FileAllowed(["jpg", "jpeg", "png", "gif"], "Image Only")])
    is_active = BooleanField("Active", default=True)
    description = TextAreaField("Description")
    fact_ids = MulticheckboxField("Facts", coerce=int)
    submit = SubmitField("Update")

    def __init__(self, original_rule: Rule, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_rule = original_rule
        self.fact_ids.choices = _fact_choices()
        if not self.is_submitted():
            self.fact_ids.data = [f.fact_id for f in original_rule.rule_facts]

    def validate_disease(self, field):
        q = db.select(Rule).filter(
            Rule.disease == field.data,
            Rule.id != self.original_rule.id,
        )
        exists = db.session.scalar(q)
        if exists:
            raise ValidationError("A disease with this name already exists.")

class RuleConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")