from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField,
                        RadioField, SubmitField,
                        TextAreaField)
from wtforms.validators import (DataRequired, NumberRange, Length)

class NewCourseForm(FlaskForm):
    title = StringField('Title',
                        validators=[DataRequired()])
    subject = StringField('Subject',
                            validators=[DataRequired()])
    points = IntegerField('Points',
                        validators=[NumberRange(max=10000)])
    code = StringField('Code',
                        validators=[DataRequired(), Length(min=4, max=36)])
    join = RadioField("Allow Users to Join",
                        validators=[DataRequired()],
                        choices=[('True', "Yes"), ('False', "No")])
    submit = SubmitField('Create')

class AddCourseForm(FlaskForm):
    course_id = IntegerField('Course ID',
                        validators=[NumberRange(max=100000000)])
    code = StringField('Code',
                        validators=[DataRequired(), Length(min=4, max=36)])
    submit = SubmitField('Add')

class UpdateCourseForm(FlaskForm):
    title = StringField('Title',
                        validators=[DataRequired()])
    subject = StringField('Subject',
                            validators=[DataRequired()])
    points = IntegerField('Points',
                        validators=[NumberRange(max=10000)])
    code = StringField('Code',
                        validators=[DataRequired(), Length(min=4, max=36)])
    join = RadioField("Allow Users to Join?",
                        validators=[DataRequired()],
                        choices=[('True', "Yes"), ('False', "No")])
    submit = SubmitField('Update')

class UpdateSyllabusForm(FlaskForm):
    syllabus = TextAreaField('Syllabus')
    submit = SubmitField('Submit')