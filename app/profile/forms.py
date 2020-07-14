from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import (StringField, TextAreaField,
                        BooleanField, SubmitField)
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_wtf.file import FileField, FileAllowed
from app.models import User_Account

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