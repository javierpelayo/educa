from flask_wtf import FlaskForm
from wtforms import (StringField, FieldList,
                    HiddenField, TextAreaField,
                    SubmitField)
from wtforms.validators import DataRequired

class NewConversationForm(FlaskForm):
    title = StringField('Conversation Title', validators=[DataRequired()])
    recipients = FieldList(HiddenField('Recipient', validators=[DataRequired()]), min_entries=1)
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class NewMessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')