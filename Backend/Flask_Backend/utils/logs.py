import logging
import colorlog

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Set the handler to default StreamHandler
    log_handler = logging.StreamHandler()
    # Set appropriate formatting for good visibility

    log_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(filename)s - %(levelname)s: %(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
            'INFO': 'light_green',
            'WARNING': 'yellow'
        }
    )
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)

    return logger