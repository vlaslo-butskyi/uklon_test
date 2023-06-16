import logging.config

from src import settings


class LevelNameFilter(logging.Filter):
    def filter(self, record):
        record.level_name = record.levelname
        return True


class ExtraFilter(logging.Filter):
    def __init__(self, param=None):
        super().__init__()
        self.param = param

    def filter(self, record):
        if not hasattr(record, "event_name"):
            record.event_name = "--"

        if not hasattr(record, "exception"):
            record.exception = "--"
        else:
            record.exception = "\nException: " + str(record.exception)
        if not hasattr(record, "traceback"):
            record.traceback = "--"
        else:
            record.traceback = "\nTraceback: " + str(record.traceback)
        return True


def configure_logger(
    service_name=settings.config.get("SERVICE_NAME"), log_level=settings.config.get("LOG_LEVEL"), handlers_list=None
):
    if handlers_list is None:
        handlers_list = ["console"]
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(levelname)s - %(event_name)s - %(message)s. %(exception)s %(traceback)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "level": log_level,
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                    "filters": ["extra_filter"],
                },
            },
            "filters": {
                "extra_filter": {
                    "()": ExtraFilter,
                    "param": "noshow",
                },
                "level_name_filter": {"()": LevelNameFilter},
            },
            "loggers": {
                service_name: {"level": log_level, "handlers": handlers_list},
            },
            "disable_existing_loggers": False,
        }
    )
    return logging.getLogger(service_name)


def service_logger():
    return configure_logger()
