from flask import jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from app.errors import HTTPError, get_object_or_404
from app.authorization import check_token, check_authorization
from app.validation import validation, CreateUser, CreateAdvertisement
from app.models import User, Advertisement
from app.settings import Session


class UserView(MethodView):
    def get(self, user_id):
        with Session() as session:
            user = get_object_or_404(session, User, User.id == user_id)
            return jsonify(user.to_dict())

    def post(self):
        with Session() as session:
            new_user = User.registration(session, **validation(request.json, CreateUser))
            try:
                session.commit()
                return jsonify(new_user.to_dict())
            except IntegrityError:
                raise HTTPError(400, 'user already exists')


class AdvertisementView(MethodView):
    def get(self, advertisement_id: int):
        with Session() as session:
            advertisement = get_object_or_404(session, Advertisement, Advertisement.id == advertisement_id)
            return jsonify(advertisement.to_dict())

    def post(self):
        advertisement_data_validated = validation(request.json, CreateAdvertisement)
        with Session() as session:
            token = check_token(session)
            if token:
                advertisement_owner = get_object_or_404(
                    session, User, User.user_name == request.headers.get('user_name')
                )
                advertisement_data_validated['owner_id'] = advertisement_owner.id
                new_advertisement = Advertisement.creation(session, **advertisement_data_validated)
                session.commit()
                return jsonify(new_advertisement.to_dict())

    def delete(self, advertisement_id: int):
        with Session() as session:
            advertisement = get_object_or_404(session, Advertisement, Advertisement.id == advertisement_id)
            check_authorization(session, advertisement)
            session.query(Advertisement).filter(Advertisement.id == advertisement_id).delete()
            session.commit()
            return jsonify({
                'message': 'your advertisement has been successfully deleted'
            })

    def put(self, advertisement_id: int):
        user_data = validation(request.json, CreateAdvertisement)
        with Session() as session:
            advertisement = get_object_or_404(session, Advertisement, Advertisement.id == advertisement_id)
            check_authorization(session, advertisement)
            advertisement.title = user_data['title']
            advertisement.description = user_data['description']
            session.commit()
            return jsonify(advertisement.to_dict())
