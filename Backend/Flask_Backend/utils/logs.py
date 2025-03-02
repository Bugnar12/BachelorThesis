import logging
import colorlog

"""
Logging module to enhance the customization of logs inside the app
"""

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        log_handler = logging.StreamHandler()
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