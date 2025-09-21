from logging.config import dictConfig

from config import DevConfig, config
import rich.pretty
import rich.traceback
import os


def configure_logging() -> None:
    # Install rich pretty and traceback handlers so objects and tracebacks are
    # rendered with Rich throughout the process.
    rich.pretty.install()
    rich.traceback.install()

    # Unified formatter used across all handlers so logs look identical.
    # Include correlation id injected by the CorrelationIdFilter.
    unified_format = "%(levelname)s [cid=%(correlation_id)s] %(filename)s:%(lineno)d - %(message)s"

    # Ensure the logs directory exists for the RotatingFileHandler
    try:
        os.makedirs("logs", exist_ok=True)
    except Exception:
        # If directory can't be created, let dictConfig fail later with
        # a clear error; we don't want to crash here during import.
        pass

    # Determine uuid length for correlation ids per environment
    uuid_length = 8 if isinstance(config, DevConfig) else 32
    # Determine how many local-part chars to show for email obfuscation
    show_local = 1 if isinstance(config, DevConfig) else 0

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "correlation.CorrelationIdFilter",
                    "uuid_length": uuid_length,
                    "default_value": "",
                }
                ,
                "email_obfuscation": {
                    "()": "logging_filters.EmailObfuscationFilter",
                    "show_local": show_local,
                    "replacement": "***",
                }
            },
            "formatters": {
                "unified": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": unified_format,
                }
                ,
                # File formatter uses JSON output via python-json-logger
                "file": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "fmt": "%(asctime)s %(levelname)s %(name)s %(correlation_id)s %(filename)s %(lineno)d %(message)s",
                }
            },
            "handlers": {
                # All handlers use RichHandler but share the same formatter
                # to ensure consistent output styling.
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "show_path": True,
                    "rich_tracebacks": True,
                    "markup": True,
                    "formatter": "unified",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "secondary": {
                    "class": "rich.logging.RichHandler",
                    "level": "INFO",
                    "show_path": True,
                    "rich_tracebacks": False,
                    "markup": True,
                    "formatter": "unified",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                # Rotating file handler for persistent logs
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "logs/app.log",
                    "maxBytes": 1048576,  # 1 MB
                    "backupCount": 3,
                    "encoding": "utf-8",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
            },
            "loggers": {
                "storeapi": {
                    "handlers": ["default"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                # databases (the `databases` package) logs queries/debug info
                "databases": {
                    "handlers": ["secondary"],
                    "level": "INFO",
                    "propagate": False,
                },
                # aiosqlite internals
                "aiosqlite": {
                    "handlers": ["secondary"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
            # Make the root logger use the rich handler so third-party
            # libraries (uvicorn, fastapi) also get Rich formatting.
            "root": {
                "handlers": ["default", "file"],
                "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
            },
            # Explicit uvicorn loggers; access uses the secondary handler
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["secondary"],
                "level": "INFO",
                "propagate": False,
            },
        }
    )
