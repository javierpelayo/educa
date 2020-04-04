from flask import (Flask, render_template,
                    request, redirect, url_for,
                    session, logging)
from flask_sqlalchemy import SQLAlchemy
from wtforms import (Form, StringField, TextAreaField,
                    PasswordField, validators)
from functools import wraps
from passlib.hash import pbkdf2_sha256
import os

# create flask app instance
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['EDUCA_SECRET_KEY']
ENV = 'dev'
# if our environ is in dev or production mode
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['EDUCA_DATABASE_URI']
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
# dont track SQLALCHEMY object mods
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#DB wraps around our app instance
db = SQLAlchemy(app)

#################
# COLOR SCHEMES #
#################
#Green: #44AF69
#Beige: #EFC7C2
#Red: #F8333C
#Yellow: #FCAB10
#Blue: #2B9EB3

##########
# ROUTES #
##########

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

###########
# FILTERS #
###########

# Queries the browser to force the
# download of an updated CSS file
@app.template_filter()
def autoversion(fn):
  fp = os.path.join('./', fn[1:])
  ts = str(os.path.getmtime(fp))
  return f"{fp}?v={ts}"

if __name__ == "__main__":
    app.run()
