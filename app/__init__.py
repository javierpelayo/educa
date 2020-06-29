from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from app.config import Config
import os

app = Flask(__name__)
# toolbar = DebugToolbarExtension()
limiter = Limiter(key_func=get_remote_address,
                default_limits=['200 per day', '50 per hour'])
db = SQLAlchemy()
bcrypt = Bcrypt()
moment = Moment()

login_manager = LoginManager()
login_manager.login_message = ""
login_manager.login_message_category = "warning"
login_manager.login_view = 'home.login'

mail = Mail()

def create_app(config_class=Config):
    pass


from . import routes
from educa.filters import autoversion
