from itsdangerous import URLSafeTimedSerializer

def get_flask_app():
    from flask import current_app
    return current_app

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(get_flask_app().config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(get_flask_app().config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email