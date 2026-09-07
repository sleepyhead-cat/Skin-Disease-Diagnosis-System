from wtforms import SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

class MulticheckboxField(SelectMultipleField):
    """Renders a list of checkboxes instead of a <select multiple>."""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
    