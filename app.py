import uuid
import datetime
import pydantic
from typing import Union
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID

app = Flask('app')
bcrypt = Bcrypt(app)
engine = create_engine('postgresql+psycopg2://flask_db_user:123@127.0.0.1:5432/flask_homework')
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(20), unique=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=False)
    registration_time = Column(DateTime, server_default=func.now())

    @classmethod
    def registration(cls, session: Session, user_name: str, email: str, password: str):
        hash_password = bcrypt.generate_password_hash(password.encode()).decode()
        new_user = User(
            user_name=user_name,
            email=email,
            password=hash_password,
        )
        session.add(new_user)
        return new_user

    def check_password(self, password: str):
        return bcrypt.check_password_hash(self.password.encode(), password.encode())

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'email': self.email,
            'registration_time': datetime.datetime.fromtimestamp(self.registration_time.timestamp()),
        }


class Advertisement(Base):

    __tablename__ = 'advertisements'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    @classmethod
    def creation(cls, session: Session, title: str, description: str, owner_id: int):
        new_advertisement = Advertisement(
            title=title,
            description=description,
            owner_id=owner_id,
        )
        session.add(new_advertisement)
        return new_advertisement

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
            'owner_id': self.owner_id,
        }


class Token(Base):

    __tablename__ = 'tokens'
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User, lazy='joined')


Base.metadata.create_all(engine)


def get_object_or_404(session, model, *criterion):
    object = session.query(model).filter(*criterion).first()
    if object is None:
        raise HTTPError(404, 'object not found')
    return object


class HTTPError(Exception):

    def __init__(self, status_code: int, message: Union[str, dict, list]):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HTTPError)
def handle_errors(error):
    response = jsonify({
        'message': error.message
    })
    response.status_code = error.status_code
    return response


def check_token(session):
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


def validation(unvalidated_data: dict, validation_model):
    try:
        return validation_model(**unvalidated_data).dict()
    except pydantic.error_wrappers.ValidationError as error:
        raise HTTPError(400, error.errors())


class CreateUser(pydantic.BaseModel):
    user_name: str
    email: str
    password: str

    @pydantic.validator('password')
    def check_password(cls, value: str):
        if len(value) < 8:
            raise ValueError('password is too short')
        return value


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


class CreateAdvertisement(pydantic.BaseModel):
    title: str
    description: str


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
                advertisement_owner = get_object_or_404(session, User, User.user_name == request.headers.get('user_name'))
                advertisement_data_validated['owner_id'] = advertisement_owner.id
                new_advertisement = Advertisement.creation(session, **advertisement_data_validated)
                session.commit()
                return jsonify(new_advertisement.to_dict())

    def delete(self, advertisement_id: int):
        with Session() as session:
            advertisement = get_object_or_404(session, Advertisement, Advertisement.id == advertisement_id)
            token = check_token(session)
            if token.user.id != advertisement.owner_id:
                raise HTTPError(403, 'auth error')
            session.query(Advertisement).filter(Advertisement.id == advertisement_id).delete()
            session.commit()
            return jsonify({
                'message': 'your advertisement has been successfully deleted'
            })

    def put(self, advertisement_id: int):
        user_data = validation(request.json, CreateAdvertisement)
        with Session() as session:
            advertisement = get_object_or_404(session, Advertisement, Advertisement.id == advertisement_id)
            token = check_token(session)
            if token.user.id != advertisement.owner_id:
                raise HTTPError(403, 'auth error')
            advertisement.title = user_data['title']
            advertisement.description = user_data['description']
            session.commit()
            return jsonify(advertisement.to_dict())


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


app.add_url_rule('/user/', methods=['POST'], view_func=UserView.as_view(name='create_user'))
app.add_url_rule('/user/<int:user_id>/', methods=['GET'], view_func=UserView.as_view(name='get_user'))
app.add_url_rule('/login/', methods=['POST'], view_func=login)
app.add_url_rule('/advertisement/', methods=['POST'], view_func=AdvertisementView.as_view(name='create_advertisement'))
app.add_url_rule('/advertisement/<int:advertisement_id>/', methods=['GET'], view_func=AdvertisementView.as_view(
    name='get_advertisement'
))
app.add_url_rule('/advertisement/<int:advertisement_id>/', methods=['DELETE'], view_func=AdvertisementView.as_view(
    name='delete_advertisement'
))
app.add_url_rule('/advertisement/<int:advertisement_id>/', methods=['PUT'], view_func=AdvertisementView.as_view(
    name='change_advertisement'
))
app.run()
