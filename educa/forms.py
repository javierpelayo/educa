from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField,
                    SubmitField, BooleanField,
                    RadioField, TextAreaField,
                    IntegerField)
from flask_login import current_user
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from educa.models import User_Account
from educa.filters import autoversion
from . import bcrypt

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

    # Raises an error if the user account already exists in our DB
    # def validate_password(self, password):
    #     user = User_Account.query.filter_by(email=self.email.data).first()
    #     user_pw = bcrypt.check_password_hash(user.password, password.data)
    #     if not user_pw:
    #         raise ValidationError("The password you entered doesn't match the email")
    #
    # def validate_email(self, email):
    #     user = User_Account.query.filter_by(email=email.data).first()
    #
    #     if not user:
    #         raise ValidationError('This user does not exist.')

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
                        validators=[DataRequired()])
    submit = SubmitField('Create')

class AddCourseForm(FlaskForm):
    id = StringField('Course ID',
                        validators=[DataRequired()])
    submit = SubmitField('Add')

class UpdateSyllabusForm(FlaskForm):
    syllabus = TextAreaField('Syllabus')
    submit = SubmitField('Submit')
