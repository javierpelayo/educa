from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField,
                    SubmitField, BooleanField,
                    RadioField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User_Account

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

# not implemented
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request')    

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                            validators=[DataRequired(),
                            Length(min=6, max=20, message="Password must be between 6 and 20 characters long.")])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(),
                            EqualTo('password')])
    submit = SubmitField('Change Password')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),
                        Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')