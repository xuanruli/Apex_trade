import logging
import os

# create logger file under logger folder
LOGS_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(LOGS_DIR, exist_ok=True)

# create log file path
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'app.log')

def get_logger():
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = get_logger()
