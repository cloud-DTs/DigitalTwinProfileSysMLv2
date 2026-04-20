import logging
import sys


def get_logger(name="sysml_code_generator", level=logging.INFO):
    logger = logging.getLogger(name)

    if len(logger.handlers) == 0:
        logger.setLevel(level)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
