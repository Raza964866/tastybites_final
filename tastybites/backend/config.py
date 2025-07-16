import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_no_one_will_ever_guess'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Door%401234@localhost/tastybites_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'syedrazah76@gmail.com'
    MAIL_PASSWORD = 'dswo gubk ocba qduy'
    MAIL_DEFAULT_SENDER = 'syedrazah76@gmail.com'
