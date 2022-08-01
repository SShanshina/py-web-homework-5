import uuid
import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.settings import app, Base, Session

bcrypt = Bcrypt(app)


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
