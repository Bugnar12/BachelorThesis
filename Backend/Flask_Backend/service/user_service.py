from repository.repository import Repository
from utils.logs import get_logger

logger = get_logger()

class UserService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)