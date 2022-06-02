from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, TextAreaField,
                    IntegerField, DateField)
from wtforms.validators import DataRequired, NumberRange

class AssignmentForm(FlaskForm):
    due_hour = []
    for hr in range(0, 24):
        if hr == 0:
            due_hour.append((str(hr), "12 a.m."))
        elif hr < 12:
            due_hour.append((str(hr), str(hr) + " a.m."))
        elif hr == 12:
            due_hour.append((str(hr), str(hr) + " p.m."))
        else:
            due_hour.append((str(hr), str(hr-12) + " p.m."))

    due_minute = [(str(min), str(min) + " mins") for min in range(0, 60)]

    title = StringField('Title', validators=[DataRequired()])
    type = SelectField('Type', choices=[('Exam/Quiz', 'Exam/Quiz'),
                                        ('Instructions', 'Instructions'),
                                        ('Lab', 'Lab'),
                                        ('HW', 'HW')])
    content = TextAreaField('Content', validators=[DataRequired()])
    points = IntegerField('Points',
                            validators=[NumberRange(max=500)])
    tries = IntegerField('Tries',
                            validators=[NumberRange(max=10)])

    date_input = DateField('Due Date', format='%Y-%m-%d')
    hour = SelectField('Hour', choices=due_hour)
    minute = SelectField('Minute', choices=due_minute)