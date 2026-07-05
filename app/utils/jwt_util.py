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
        'sub': str(user_id)  # JWT spec requires 'sub' to be a string
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY", "default_secret_key"), algorithm='HS256')

def decode_jwt(token):
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY", "default_secret_key"), algorithms=['HS256'])
        return int(payload['sub'])  # Convert back to int for the application
    except jwt.ExpiredSignatureError as e:
        print(f"Token expired: {e}")
        return None  # Token expired
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None  # Invalid token
    except Exception as e:
        print(f"Unknown JWT error: {e}")
        return None
