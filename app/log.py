import logging
from logging import Logger


def get_logger(name: str | None = None) -> Logger:

    logging.basicConfig(level=logging.DEBUG,
                        format="[%(asctime)s] : [%(levelname)s] : [%(name)s] :  стр %(lineno)s : %(message)s",
                        datefmt="%Y.%m.%d %H:%M:%S")
    logger = logging.getLogger(name=name if name else __name__)
    return logger


if __name__ == '__main__':
    logger: Logger = get_logger("log.py")
    logger.debug("Информационное сообщение уровня DEBUG")
    logger.info("Информационное сообщение уровня INFO")
