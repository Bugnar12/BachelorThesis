# Will use dependency injection for avoiding loosely coupled modules
from model.user import User


class UserService:
    def __init__(self, db_session):
        self.db = db_session

    def get_all_users(self):
        return User.query.all()