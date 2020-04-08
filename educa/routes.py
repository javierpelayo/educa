from flask import (render_template,request,
                    redirect, url_for,
                    session, logging, current_app)
from . import app, bcrypt
from educa.forms import RegistrationForm, LoginForm
from functools import wraps
from educa.filters import autoversion

# 1. MAIN STAGE - INTRODUCTION PAGES
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

# 2. SUB-STAGE
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    # if the form is validated on submit
    if request.method == 'POST' and form.validate_on_submit():
        # User DB entry here
        return redirect(url_for('home'))
    return render_template("register.html", title="Register",
                            form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('home'))
    return render_template("login.html", title="Login", form=form)
