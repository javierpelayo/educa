from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField,
                    SubmitField, BooleanField,
                    RadioField, TextAreaField,
                    IntegerField, DateField,
                    SelectField, FieldList,
                    HiddenField)
from flask_login import current_user
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from educa.models import User_Account
from educa.filters import autoversion
from . import bcrypt
from pytz import common_timezones

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name',
                        validators=[DataRequired(),
                        Length(min=1, max=120)])
    last_name = StringField('Last Name',
                        validators=[DataRequired(),
                        Length(min=1, max=120)])
    email = StringField('Email',
                        validators=[DataRequired(),
                        Email()])
    password = PasswordField('Password',
                            validators=[DataRequired(),
                            Length(min=6, max=20, message="Password must be between 6 and 20 characters long.")])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(),
                            EqualTo('password')])
    profession = RadioField('I am a', choices=[('Student', 'Student'), ('Teacher', 'Teacher')])
    submit = SubmitField('Sign Up')

    # Raises an error if the user account already exists in our DB
    def validate_email(self, email):
        user = User_Account.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('A user with that email already exists.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),
                        Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    fullname = StringField('Full Name',
                        validators=[DataRequired(),
                        Length(min=1, max=240)])
    email = StringField('Email',
                        validators=[DataRequired(),
                        Email()])
    biography = TextAreaField('Bio', validators=[Length(max=240)])
    picture = FileField('Choose File',
                        validators=[FileAllowed(['jpg', 'png'], "Only jpg or png file-types allowed.")])
    removepic = BooleanField('Remove Profile Picture')
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User_Account.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('A user with that email already exists.')

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

class AssignmentForm(FlaskForm):
    # refactor
    due_hour = [('0','12 a.m.'), ('1','1 a.m.'), ('2', '2 a.m.'), ('3', '3 a.m.'), ('4', '4 a.m.'), ('5', '5 a.m.'),
                ('6', '6 a.m.'), ('7', '7 a.m.'), ('8', '8 a.m.'), ('9', '9 a.m.'), ('10', '10 a.m.'),
                ('11', '11 a.m.'), ('12', '12 p.m.'), ('13', '1 p.m.'), ('14', '2 p.m.'), ('15', '3 p.m.'),
                ('16', '4 p.m.'), ('17', '5 p.m.'), ('18', '6 p.m.'), ('19', '7 p.m.'), ('20', '8 p.m.'),
                ('21', '9 p.m.'), ('22', '10 p.m.'), ('23', '11 p.m.')]
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

    date_input = DateField('Due Date', format='%m/%d/%Y')
    hour = SelectField('Hour', choices=due_hour)
    minute = SelectField('Minute', choices=due_minute)
