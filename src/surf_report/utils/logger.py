import logging

# Constants
LOG_LEVEL = logging.NOTSET
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE = "surf_report.log"
LOG_FILE_MODE = "a"


def setup_logger():
    # Logger configuration
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        filename=LOG_FILE,
        filemode=LOG_FILE_MODE,
    )
