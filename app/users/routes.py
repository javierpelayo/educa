from flask import (Blueprint, redirect, url_for,
                    request, render_template, flash)
from flask_login import current_user, login_user, logout_user
from app import db, bcrypt
from app.users.forms import (RegistrationForm, ResetPasswordRequestForm,
                                ResetPasswordForm, LoginForm)
from app.users.email import (send_email, send_email_confirmation,
                                send_password_reset)
from app.models import User_Account
from app.filters import autoversion

users = Blueprint("users", __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))
    form = RegistrationForm()
    # if the form is validated on submit
    if request.method == 'POST' and form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User_Account(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    profession=form.profession.data,
                    password=hashed_pw,
                    confirmed=False)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users.verify_email_message', email=form.email.data))
    else:
        return render_template("register.html", title="Register",
                                form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User_Account.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.confirmed:
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                # if next_page query parameter exists redirect to that page
                return redirect(next_page) if next_page else redirect(url_for('home.home'))
            else:
                return redirect(url_for('users.verify_email_message', email=user.email))
        else:
            error = "The email or password is incorrect."
            return render_template("login.html",
                                    title="Login",
                                    form=form,
                                    error=error)
    return render_template("login.html",
                            title="Login",
                            form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.home'))

@users.route('/verify_email_message/<string:email>', methods=["GET"])
def verify_email_message(email):
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('courses.dashboard'))
    if request.method == "GET":
        user = User_Account.query.filter_by(email=email).first()
        if user:
            if not user.confirmed:
                send_email_confirmation(user)
                return render_template("verify_email.html", email=email, title="Email Confirmation")
            else:
                flash("Your email has been confirmed.", "success")
                return redirect(url_for('users.login'))
        else:
            flash("A user with that email does not exist.", "danger")
            return redirect(url_for('users.login'))

@users.route('/resend_email_message/<string:email>', methods=["GET"])
def resend_email_message(email):
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('courses.dashboard'))

    # Not following DRY incase of flash message pile up
    if request.method == "GET":
        user = User_Account.query.filter_by(email=email).first()
        if user:
            if not user.confirmed:
                flash("Your email confirmation link has been resent.", "success")
                return redirect(url_for("users.verify_email_message", email=email))
            else:
                flash("Your email has been confirmed.", "success")
                return redirect(url_for('users.login'))
        else:
            flash("A user with that email does not exist.", "danger")
            return redirect(url_for('users.login'))


@users.route('/verify_email/<token>', methods=["GET", "POST"])
def verify_email(token):
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('courses.courses'))
    user = User_Account.verify_token(token)
    if not user:
        flash("This email verification link has expired. Please try again by logging in.", "warning")
        return redirect(url_for('users.login'))
    if request.method == "GET":
        user.confirmed = True
        db.session.commit()
        flash("Your email has been confirmed.", "success")
        return redirect(url_for('users.login'))



@users.route('/reset_password_request', methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('courses.courses'))
    form = ResetPasswordRequestForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User_Account.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset(user)
            return render_template("reset_password_message.html", email=user.email, title="Reset Password")
        else:
            flash("That user does not exist. Please register an account if you haven't.", "warning")
            return redirect(url_for("users.reset_password_request"))
    else:
        return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@users.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('courses.courses'))
    user = User_Account.verify_token(token)
    if not user:
        flash("The link to reset your password has expired. Please try again.", "warning")
        return redirect(url_for('users.login'))
    form = ResetPasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash("Your password has been reset.", "success")
        return redirect(url_for('users.login'))
    else:
        return render_template('reset_password.html', form=form, title="Reset Password")