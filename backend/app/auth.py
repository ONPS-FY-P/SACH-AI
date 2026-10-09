import time
import jwt
from fastapi import Header, HTTPException
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from . import config

ISSUER = 'naaya-api'
AUDIENCE = 'naaya-mobile'

def verify_google(token):
    if not config.GOOGLE_WEB_CLIENT_ID or len(config.JWT_SECRET) < 32:
        raise HTTPException(503, 'Google login is not configured on the server.')
    try:
        claims = id_token.verify_oauth2_token(token, Request(), config.GOOGLE_WEB_CLIENT_ID)
        if not claims.get('email_verified') or not claims.get('sub'):
            raise ValueError('Unverified account')
        return {'id': claims['sub'], 'name': claims.get('name', 'User'), 'email': claims.get('email', '')}
    except ValueError:
        raise HTTPException(401, 'Google token is invalid or expired.') from None
    except Exception:
        raise HTTPException(503, 'Google verification is temporarily unavailable.') from None

def issue_session(user):
    now = int(time.time())
    return jwt.encode({**user, 'sub': user['id'], 'iat': now, 'exp': now + 3600,
                       'iss': ISSUER, 'aud': AUDIENCE}, config.JWT_SECRET, algorithm='HS256')

def read_session(authorization):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, 'Please sign in to continue.')
    if len(config.JWT_SECRET) < 32:
        raise HTTPException(503, 'Sessions are not configured on the server.')
    try:
        return jwt.decode(authorization[7:], config.JWT_SECRET, algorithms=['HS256'],
                          issuer=ISSUER, audience=AUDIENCE,
                          options={'require': ['exp', 'iat', 'sub', 'iss', 'aud']})
    except jwt.PyJWTError:
        raise HTTPException(401, 'Your session expired. Please sign in again.') from None

def optional_user(authorization: str | None = Header(default=None)):
    if authorization:
        return read_session(authorization)
    if config.REQUIRE_AUTH:
        raise HTTPException(401, 'Please sign in to use the assistant.')
    return None
