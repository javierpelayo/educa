from flask import (render_template,request,
                    redirect, url_for,
                    session, logging, current_app)
from . import app, bcrypt
from educa.filters import autoversion
from educa.forms import RegistrationForm, LoginForm
from functools import wraps

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

# 2. SUB-STAGE LOGIN PORTAL
@app.route('/portal')
def portal():
    return render_template("portal.html", title="Portal")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    # if the form is validated on submit
    if form.validate_on_submit():
        return redirect(url_for('home'))
    print(form.hidden_tag())
    return render_template("register.html", title="Register",
                            form=form)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template("login.html", title="Login",
                            form=form)
