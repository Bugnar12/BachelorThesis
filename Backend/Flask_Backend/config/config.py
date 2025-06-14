import json
import os
import tempfile

from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL_DEPLOY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('FLASK_JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=30)
    VT_API_KEY = os.environ.get('VIRUSTOTAL_API_KEY')

class GmailConfig:
    @staticmethod
    def get_secret_file_path():
        data = os.environ.get("GMAIL_CLIENT_SECRET")
        if not data:
            raise RuntimeError("GMAIL_CLIENT_SECRET env var is missing")

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
        json.dump(json.loads(data), temp)
        temp.close()
        return temp.name
    GMAIL_SCOPE = ["https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ]
    REDIRECT_URI = os.environ.get('GMAIl_REDIRECT_URI', "https://bachelorthesis-production-8acf.up.railway.app/gmail/oauth2callback")
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