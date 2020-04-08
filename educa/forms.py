from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField,
                    SubmitField, BooleanField,
                    RadioField)
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name',
                        validators=[DataRequired(),
                        Length(min=1, max=20)])
    last_name = StringField('Last Name',
                        validators=[DataRequired(),
                        Length(min=1, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(),
                        Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(),
                            EqualTo('password')])
    profession = RadioField('I am a', choices=[('Student', 'Student'), ('Teacher', 'Teacher')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),
                        Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CourseForm(FlaskForm):
    pass
