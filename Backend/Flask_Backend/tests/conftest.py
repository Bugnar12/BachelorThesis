import sys
import os
import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db

@pytest.fixture(scope="session")
def test_app():
    # Configure the app for testing with SQLite in-memory DB
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app):
    with test_app.test_client() as client:
        yield client


@pytest.fixture
def auth_header(test_app):
    with test_app.app_context():
        token = create_access_token(identity='user1')
    return {'Authorization': f'Bearer {token}'}

from model.user import User

@pytest.fixture
def seed_user(db_session):
    user = User(user_name='Test User', user_email='test@example.com')
    db_session.add(user)
    db_session.commit()
    return user

