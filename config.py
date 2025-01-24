from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://ares:1234@localhost/wordle'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = getenv("SECRET_KEY")