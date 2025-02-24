from flask import Flask

from utils.logs import get_logger

app = Flask(__name__)
logger = get_logger()

@app.route('/')
def hello_world():  # put application's code here
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.exception("This is an exception message")
    logger.error("This is an error message")
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
