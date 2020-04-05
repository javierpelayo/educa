from flask import (render_template,request,
                    redirect, url_for,
                    session, logging)
from . import app, bcrypt
from functools import wraps

# 1. MAIN STAGE - INTRODUCTION PAGES
@app.route('/')
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
