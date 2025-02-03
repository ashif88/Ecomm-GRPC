import jwt,os
import datetime

def generate_jwt(user_id):
    """Generate a JWT token for user authentication."""
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=os.getenv("JWT_ACCESS_TOKEN_EXPIRES")),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY",""), algorithm='HS256')

def decode_jwt(token):
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
