from logging.config import dictConfig

from config import DevConfig, config
import rich.pretty
import rich.traceback


def configure_logging() -> None:
    # Install rich pretty and traceback handlers so objects and tracebacks are
    # rendered with Rich throughout the process.
    rich.pretty.install()
    rich.traceback.install()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                # Keep a formatter that includes filename and line number so
                # the RichHandler output includes that context.
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(filename)s:%(lineno)d - %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    # Let RichHandler receive extra options to show path
                    # and enable markup. These kwargs are forwarded to the
                    # RichHandler constructor by dictConfig.
                    "show_path": True,
                    "rich_tracebacks": True,
                    "markup": True,
                    "formatter": "console",
                }
            },
            "loggers": {
                "storeapi": {
                    "handlers": ["default"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                }
            },
            # Make the root logger use the rich handler so third-party
            # libraries (uvicorn, fastapi) also get Rich formatting.
            "root": {
                "handlers": ["default"],
                "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
            },
            # Ensure uvicorn-related loggers don't bypass the root handler.
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
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        }
    )
