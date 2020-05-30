from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

# create flask app instance
app = Flask(__name__)
limiter = Limiter(app,
                key_func=get_remote_address,
                default_limits=['200 per day', '50 per hour'])
app.config['SECRET_KEY'] = os.environ['EDUCA_SECRET_KEY']
# toolbar = DebugToolbarExtension(app)
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
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_message = ""
login_manager.login_message_category = "warning"
# Tells the extension where our login route is located
# redirects the user to the login route
login_manager.login_view = 'login'

from . import routes
from educa.filters import autoversion
