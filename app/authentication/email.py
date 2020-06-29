from flask import render_template
from flask_mail import Message
from . import mail

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_email_confirmation(user):
    token = user.get_token(expires_in=60)
    send_email(subject="EDUCA - Email Confirmation",
                sender="contact@javierperez.dev",
                recipients=[user.email],
               text_body=render_template('email/verify_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/verify_email.html',
                                         user=user, token=token))

def send_password_reset(user):
    token = user.get_token(expires_in=600)
    send_email(subject="EDUCA - Password Reset",
                sender="contact@javierperez.dev",
                recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))