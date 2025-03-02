import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    MXTOOLBOX_API_KEY = os.getenv('MXTOOLBOX_API_KEY')