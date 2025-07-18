import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_no_one_will_ever_guess'
    
    # This will be updated with PythonAnywhere's MySQL details
    # Format: mysql://username:password@username.mysql.pythonanywhere-services.com/username$tastybites_db
    SQLALCHEMY_DATABASE_URI = 'mysql://raza786:Y_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    # Email configuration (you can keep these the same)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'sym'
    MAIL_PASSWORD = 'dduy'
    MAIL_DEFAULT_SENDER = 'scom'
