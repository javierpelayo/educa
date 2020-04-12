from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
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
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# Tells the extension where our login route is located
# redirects the user to the login route
login_manager.login_view = 'login'

from . import routes
from educa.filters import autoversion

#################
# COLOR SCHEMES #
#################
#Green: #44AF69
#Beige: #EFC7C2
#Red: #F8333C
#Yellow: #FCAB10
#Blue: #2B9EB3
