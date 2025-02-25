from model.user import User
from werkzeug.security import generate_password_hash, check_password_hash

from repository.repository import Repository
from utils.logs import get_logger

logger = get_logger()

# TODO: add graceful error handling + validation
# Will use dependency injection for avoiding loosely coupled modules
class UserService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)

    def register_user(self, user_data):
        user = User()
        user.from_dict(user_data)
        user.user_password = generate_password_hash(user.user_password)
        logger.info("Adding user {}".format(user))
        return self.__repository.add_user(user)


    def login_user(self, user_data):
        user = self.__repository.find_by_email(user_data['email'])
        if user and check_password_hash(user.user_password, user_data['password']):
            logger.info("Logging in user: {}".format(user))
            return user
        return None