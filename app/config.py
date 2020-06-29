import configparser

config = configparser.ConfigParser()
config.read('educa/config.ini')

class Config:
    SECRET_KEY = config['DEFAULT']['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = config['DEFAULT']['DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 500 * 1024
    MAIL_SERVER = 'mail.privateemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = config['DEFAULT']['EMAIL_USER']
    MAIL_PASSWORD = config['DEFAULT']['EMAIL_PASSWORD']