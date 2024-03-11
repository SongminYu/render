import logging


def get_logger(name, level=logging.INFO, file_name: str = None):
    logging.basicConfig()
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
