# app/logger.py

import os
import logging
import json
from logging.handlers import RotatingFileHandler

class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON with standardized security event attributes.
    """
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%SZ"),
            "event_id": getattr(record, 'event_id', record.levelname),
            "user_id": getattr(record, 'user_id', None),
            "ip_address": getattr(record, 'ip_address', None),
            "component": getattr(record, 'component', None),
            "outcome": getattr(record, 'outcome', None),
            "message": record.getMessage(),
            "extra": getattr(record, 'extra', {})
        }
        return json.dumps(log_record)

def setup_logging(app=None):
    """
    Configures and returns a 'echelon' logger with:
      - A rotating file handler at a configurable path (LOG_PATH or ./logs/security.log)
      - A console (stdout) handler for container platforms
    """
    # Determine log path from Flask config or fallback to ./logs/security.log
    if app and app.config.get('LOG_PATH'):
        log_path = app.config['LOG_PATH']
    else:
        base = os.getcwd()
        log_path = os.path.join(base, 'logs', 'security.log')

    # Ensure the directory exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Create and configure logger
    logger = logging.getLogger('echelon')
    logger.setLevel(logging.INFO)

    # Rotating file handler
    fh = RotatingFileHandler(log_path, maxBytes=5_242_880, backupCount=5)
    fh.setFormatter(JSONFormatter())
    logger.addHandler(fh)

    # Console handler (stdout)
    ch = logging.StreamHandler()
    ch.setFormatter(JSONFormatter())
    logger.addHandler(ch)

    return logger
