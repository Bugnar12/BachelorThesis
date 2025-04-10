import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    MXTOOLBOX_API_KEY = os.getenv('MXTOOLBOX_API_KEY')


class GmailConfig:
    CLIENT_SECRET_FILE = os.getenv('GMAIL_CLIENT_SECRET')
    GMAIL_SCOPE = ['https://www.googleapis.com/auth/gmail.readonly']
    REDIRECT_URI = os.getenv('GMAIl_REDIRECT_URI', "http://localhost:5000/gmail/oauth2callback")
    GMAIL_SUBSCRIPTION_TOPIC = r"projects/infra-inkwell-454717-t0/topics/gmail-incoming-emails"