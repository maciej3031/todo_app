from wtforms import SubmitField, HiddenField
from flask_wtf import Form


class TaskForm(Form):
    executed_button = SubmitField("Execute!")
    erase_button = SubmitField("Delete Task")
