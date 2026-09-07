# app/forms/diagnose_form.py
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, FieldList, FormField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Optional

class SymptomSeverityForm(FlaskForm):
    """Sub-form for individual symptom severity selection."""
    class Meta:
        csrf = False  # Main form handles CSRF protection

    fact_id = IntegerField('Fact ID', validators=[DataRequired()])
    # Severity values: 0.0 = Absent/Not selected, 0.3 = Mild, 0.6 = Moderate, 0.9 = Severe
    severity = SelectField(
        'Severity',
        choices=[
            ('0.0', 'None / Mild Concern'),
            ('0.3', 'Mild'),
            ('0.6', 'Moderate'),
            ('0.9', 'Severe')
        ],
        default='0.6'
    )

class DiagnoseForm(FlaskForm):
    """Main Diagnosis Form."""
    submit = SubmitField('Run Diagnosis')