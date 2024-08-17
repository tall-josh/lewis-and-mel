import logging
from pathlib import Path
import json
from logging.handlers import TimedRotatingFileHandler
import os

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'level': record.levelname,
            'time': self.formatTime(record, self.datefmt),
            'name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        return json.dumps(log_record)

def get_logger():
    logger = logging.getLogger('main_logger')

    log_levels = {"WARNING": logging.WARNING,
                  "DEBUG": logging.DEBUG,
                  "ERROR": logging.ERROR,
                  "INFO": logging.INFO,
                  }
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_level = log_levels[log_level]
    logger.setLevel(log_level)
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    
    # File handler that rotates every hour

    logs_dir = "data/logs"
    Path(logs_dir).mkdir(exist_ok=True)
    file_handler = TimedRotatingFileHandler(f'{logs_dir}/my_log.log', when='H', interval=1, backupCount=24*7)  # Keeps the last 7d of logs
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

