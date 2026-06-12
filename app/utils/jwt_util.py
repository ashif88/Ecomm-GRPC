import jwt,os
import datetime

def generate_jwt(user_id):
    """Generate a JWT token for user authentication."""
    try:
        expires_seconds = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
    except (TypeError, ValueError):
        expires_seconds = 3600

    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_seconds),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY", "default_secret_key"), algorithm='HS256')

def decode_jwt(token):
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY", "default_secret_key"), algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
