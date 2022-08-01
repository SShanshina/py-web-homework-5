from flask import jsonify, request
from app.errors import HTTPError, get_object_or_404
from app.validation import validation, CreateUser
from app.models import User, Token
from app.settings import Session


def login():
    user_data = validation(request.json, CreateUser)
    with Session() as session:
        user = get_object_or_404(session, User, User.user_name == user_data['user_name'])
        if not user.check_password(user_data['password']):
            raise HTTPError(401, 'wrong password')
        new_token = Token(user_id=user.id)
        session.add(new_token)
        session.commit()
        return jsonify({
            'message': 'login successful',
            'token': new_token.id,
        })
