from model.user import User


class Repository:

    def __init__(self, database):
        self.__db = database

    """
    Adds a user to the database
    """
    def add_user(self, added_user):
        self.__db.session.add(added_user)
        self.__db.session.commit()
        return added_user

    """
    Finds a user by its email and returns it
    """
    def find_by_email(self, email):
        return self.__db.query(User).filter_by(email=email).first()
