from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators


class TextForm(FlaskForm):
    text = TextAreaField('Text:', validators=[validators.required()])

    def validate(self):
        if not self.text.validate(self):
            return False
        return True
