from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.fact import Fact
from extensions import db

class FactCreateForm(FlaskForm):
    symptom = StringField(
        "Symptom",
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={"placeholder": "e.g. Redness, Blister"},
    )
    description = TextAreaField(
        "Description",
        render_kw={"placeholder": "More information about the symptom."},
    )
    submit = SubmitField("Save")

    def validate_symptom(self, field):
        exists = db.session.scalar(
            db.select(Fact).filter(Fact.symptom == field.data)
        )
        if exists:
            raise ValidationError("A symptom with this name already exists.")


class FactEditForm(FlaskForm):
    symptom = StringField(
        "Symptom",
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={"placeholder": "Update symptom name"},
    )
    description = TextAreaField(
        "Description",
        render_kw={"placeholder": "Update description"},
    )

    submit = SubmitField("Update")

    def __init__(self, *args, original_fact=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_fact = original_fact

    def validate_symptom(self, field):
        # Ignore uniqueness validation if the symptom name hasn't changed
        if self.original_fact and field.data == self.original_fact.symptom:
            return

        query = db.select(Fact).filter(Fact.symptom == field.data)
        if self.original_fact:
            query = query.filter(Fact.id != self.original_fact.id)

        exists = db.session.scalar(query)
        if exists:
            raise ValidationError("A symptom with this name already exists.")


class FactConfirmDeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")