from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://flask_db_user:123@127.0.0.1:5432/flask_homework')
Base = declarative_base()
Session = sessionmaker(bind=engine)

app = Flask(__name__)
