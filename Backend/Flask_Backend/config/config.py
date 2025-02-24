import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # TODO: replace with actual credentials
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URL", "postgresql://user:password@localhost:5432/db_name")