from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
import configparser
import os

app = Flask(__name__)
limiter = Limiter(app,
                key_func=get_remote_address,
                default_limits=['200 per day', '50 per hour'])

config = configparser.ConfigParser()
config.read('educa/config.ini')

app.config['SECRET_KEY'] = config['DEFAULT']['SECRET_KEY']
# toolbar = DebugToolbarExtension(app)
app.config['SQLALCHEMY_DATABASE_URI'] = config['DEFAULT']['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
moment = Moment(app)

login_manager = LoginManager(app)
login_manager.login_message = ""
login_manager.login_message_category = "warning"
login_manager.login_view = 'login'

app.config['MAIL_SERVER'] = 'mail.privateemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config['DEFAULT']['EMAIL_USER']
app.config['MAIL_PASSWORD'] = config['DEFAULT']['EMAIL_PASSWORD']
mail = Mail(app)


from . import routes
from educa.filters import autoversion
