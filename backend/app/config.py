import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


class Config:
    SECRET_KEY = os.getenv('secret', 'fallback-secret')
    API_KEY = os.getenv('api_key', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = '{conn}://{user}:{pw}@{host}:{port}/{db}'.format(
        conn=os.getenv('connection', 'postgresql'),
        user=os.getenv('username', ''),
        pw=os.getenv('password', ''),
        host=os.getenv('dsn', '127.0.0.1'),
        port=os.getenv('port', '5432'),
        db=os.getenv('database', ''),
    )
