from flask import request
from app.errors import HTTPError
from app.models import User, Advertisement, Token, Session


def check_token(session: Session):
    token = (
        session.query(Token)
        .join(User)
        .filter(
            User.user_name == request.headers.get('user_name'),
            Token.id == request.headers.get('token'),
        )
        .first()
    )
    if token is None:
        raise HTTPError(401, 'invalid token or user name')
    return token


def check_authorization(session: Session, advertisement: Advertisement):
    token = check_token(session)
    if token.user.id != advertisement.owner_id:
        raise HTTPError(403, 'auth error')
