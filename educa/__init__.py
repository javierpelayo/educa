from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
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
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from educa.filters import autoversion
from . import routes

#################
# COLOR SCHEMES #
#################
#Green: #44AF69
#Beige: #EFC7C2
#Red: #F8333C
#Yellow: #FCAB10
#Blue: #2B9EB3
