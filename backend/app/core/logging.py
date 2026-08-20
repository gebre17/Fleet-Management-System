"""Structured (JSON) logging configuration.

Plain text logs are hard to search/aggregate once this runs as more than
one container. JSON logs work directly with any log aggregator (Docker's
own json-file driver, CloudWatch, Loki, etc.) without extra parsing.
"""

import logging

from pythonjsonlogger import jsonlogger

from app.core.config import settings


def configure_logging() -> None:
    """Replace the default logging config with a JSON formatter."""
    handler = logging.StreamHandler()
    handler.setFormatter(
        jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        )
    )

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.LOG_LEVEL)
