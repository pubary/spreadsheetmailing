import logging.config

from config import MY_DEBUG, LOG_NAME


logger = logging.getLogger(__name__)
logfile = f'{LOG_NAME}.log'

if MY_DEBUG:
    MY_LEVEL = 'DEBUG'
else:
    MY_LEVEL = 'INFO'

LOGGING_CONF = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "level": MY_LEVEL,
            "formatter": "simple",
            "filename": logfile,
            "encoding": "utf8"
        },
    },
    "root": {
        "level": MY_LEVEL,
        "handlers": ["file_handler"]
    }
}

logging.config.dictConfig(LOGGING_CONF)
