import json
import logging
from logging import Logger
from typing import Any, Optional

from pydantic import Field

from livekit_voice_call_runner.model import BaseModel

_DENY_LIST_EXTRA_KEYS = [
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "getMessage",
    "stack_info",
    "correlation_id",
]


class JsonLogRecord(BaseModel):
    timestamp: str
    level: str
    logger: str
    message: str
    correlation_id: Optional[str] = None
    extra: dict[str, Any] = Field(default_factory=dict)

    def model_dump(self, **kwargs) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "logger": self.logger,
            "message": self.message,
            "correlation_id": self.correlation_id,
            **self.extra,
        }


class JsonFormatter(logging.Formatter):
    def __init__(self, correlation_id: Optional[str] = None, pretty_print: Optional[bool] = None):
        super().__init__()
        self.correlation_id = correlation_id
        self.pretty_print = pretty_print

    def format(self, record: logging.LogRecord) -> str:
        # map record to log data
        json_record = JsonLogRecord(
            timestamp=self.formatTime(record),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            correlation_id=self.correlation_id,
        )

        # add extra fields
        for key, value in record.__dict__.items():
            if key not in _DENY_LIST_EXTRA_KEYS and value not in [None, ""]:
                json_record.extra[key] = value

        json_record_dict = json_record.model_dump()
        if self.pretty_print:
            return json.dumps(json_record_dict, indent=2)
        return json.dumps(json_record_dict)


class ColoredJsonFormatter(JsonFormatter):
    def __init__(self, correlation_id: Optional[str] = None, pretty_print: Optional[bool] = None):
        super().__init__(correlation_id=correlation_id, pretty_print=pretty_print)
        self._colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[31m",  # Red
        }
        self._reset = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        json_record = JsonFormatter.format(self, record)

        if record.levelname in self._colors:
            color = self._colors[record.levelname]
            json_record = json_record.replace(
                f'"level": "{record.levelname}"', f'"level": "{color}{record.levelname}{self._reset}"'
            )
        return json_record


class CallLogger(Logger):
    def __init__(self, name: str, correlation_id: Optional[str] = None):
        super().__init__(name=name)
        self._correlation_id = correlation_id

    @property
    def correlation_id(self) -> Optional[str]:
        return self._correlation_id


def create_logger(
    name: str,
    correlation_id: Optional[str] = None,
    pretty_print: Optional[bool] = False,
) -> CallLogger:
    logger = CallLogger(name=name, correlation_id=correlation_id)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(ColoredJsonFormatter(correlation_id=correlation_id, pretty_print=pretty_print))
    logger.addHandler(handler)
    return logger
