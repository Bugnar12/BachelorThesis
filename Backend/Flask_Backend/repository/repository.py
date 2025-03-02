from model.user import User

from utils.logs import get_logger

logger = get_logger()

class Repository:

    def __init__(self, database):
        self.__db = database

    """
    Adds a user to the database
    """
    def add_user(self, added_user):
        self.__db.add(added_user)
        self.__db.commit()
        return added_user

    """
    Finds a user by its email and returns it
    """
    def find_by_email(self, email):
        logger.info("Found user")
        return self.__db.query(User).filter_by(user_email=email).first()

    def save_email(self, email):
        self.__db.add(email)
        self.__db.commit()
        return email
