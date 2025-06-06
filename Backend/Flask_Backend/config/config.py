import os

from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL_DEPLOY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('FLASK_JWT_SECRET_KEY')
    # TODO: MODIFY THIS AFTER TESTING TO A LONGER TIME
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=31)
    VT_API_KEY = os.getenv('VIRUSTOTAL_API_KEY')

class GmailConfig:
    CLIENT_SECRET_FILE = os.getenv('GMAIL_CLIENT_SECRET')
    GMAIL_SCOPE = ["https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
    ]
    REDIRECT_URI = os.getenv('GMAIl_REDIRECT_URI', "http://localhost:5000/gmail/oauth2callback")
    GMAIL_SUBSCRIPTION_TOPIC = r"projects/infra-inkwell-454717-t0/topics/gmail-incoming-emails"

class HFConfig:
    HF_API_TOKEN = os.getenv('HUGGING_FACE_API_TOKEN')

class VAPIDConfig:
    VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY')
    VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY')
    VAPID_CLAIMS = {
        "sub": "mailto:eduardbugnaru@gmail.com"
    }
    FCM_API_KEY = os.getenv('FCM_API_KEY')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret"