from flask import (render_template,request,
                    redirect, url_for,
                    session, logging, current_app)
from . import app, bcrypt
from educa.forms import RegistrationForm, LoginForm
from educa.filters import autoversion
from educa.models import *
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps

# INTRODUCTION PAGES

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", title="Home")

@app.route('/about')
def about():
    return render_template("about.html", title="About")

@app.route('/packages')
def packages():
    return render_template("packages.html", title="Packages")

# REGISTER / LOGIN / LOGOUT

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    # if the form is validated on submit
    if request.method == 'POST' and form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User_Account(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    profession=form.profession.data,
                    password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        # User DB entry here
        return redirect(url_for('home'))
    else:
        return render_template("register.html", title="Register",
                                form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User_Account.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print("Login Successful")
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # if next_page query parameter exists redirect to that page
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            error = "The email or password is incorrect."
            return render_template("login.html", title="Login", form=form, error=error)
    else:
        return render_template("login.html", title="Login", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# DASHBOARD

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@app.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('dashboard.html', title='Dashboard')
