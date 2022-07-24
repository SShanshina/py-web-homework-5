import datetime
import pydantic
from typing import Union
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    owner_id = Column(Integer, ForeignKey(User.id))


Base.metadata.create_all(engine)


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


class RegisterUser(pydantic.BaseModel):
    user_name: str
    email: str
    password: str

    @pydantic.validator('password')
    def check_password(cls, value: str):
        if len(value) < 8:
            raise ValueError('password is too short')
        return value


def validation(unvalidated_data: dict, validation_model):
    try:
        return validation_model(**unvalidated_data).dict()
    except pydantic.error_wrappers.ValidationError as error:
        raise HTTPError(400, error.errors())


def get_object_or_404(session, model, *criterion):
    user = session.query(model).filter(*criterion).first()
    if user is None:
        raise HTTPError(404, 'user not found')
    return user


class UserView(MethodView):
    def get(self, user_id):
        with Session() as session:
            user = get_object_or_404(session, User, User.id == user_id)
            return jsonify(user.to_dict())

    def post(self):
        with Session() as session:
            new_user = User.registration(session, **validation(request.json, RegisterUser))
            try:
                session.commit()
                return jsonify(new_user.to_dict())
            except IntegrityError:
                raise HTTPError(400, 'user already exists')

# class AdvertisementView(MethodView):
#     def get(self, advertisement_id: int):
#         with Session() as session:
#             pass
#
#     def post(self):
#         advertisement_data = request.json
#         with Session() as session:
#             new_advertisement = Advertisement(
#                 title=advertisement_data['title'],
#                 description=advertisement_data['description'],
#                 owner_id=User.id,
#             )
#             session.add(new_advertisement)
#             session.commit()


def login():
    user_data = validation(request.json, RegisterUser)
    with Session() as session:
        user = get_object_or_404(session, User, User.user_name == user_data['user_name'])
        if not user.check_password(user_data['password']):
            raise HTTPError(401, 'wrong password')
        return jsonify({
            'message': 'login successful'
        })


app.add_url_rule('/user/', methods=['POST'], view_func=UserView.as_view(name='create_user'))
app.add_url_rule('/user/<int:user_id>/', methods=['GET'], view_func=UserView.as_view(name='get_user'))
app.add_url_rule('/login/', methods=['POST'], view_func=login)
app.run()
