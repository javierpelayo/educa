from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SubmitField)
from wtforms.validators import DataRequired

class NewLectureForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    url = StringField('Video Url', validators=[DataRequired()])
    description = TextAreaField('Video Url', validators=[DataRequired()])
    submit = SubmitField('Submit')