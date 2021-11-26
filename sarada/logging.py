"""
Setup for logging in the application.
"""
from __future__ import annotations

import logging
import os

from types import FrameType
from typing import Optional

from loguru import logger


class InterceptHandler(logging.Handler):
    """Intercept logs from logging and forward to loguru sinks."""

    def emit(self, record):  # type: ignore
        """Log emited logs with loguru sinks."""
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame: Optional[FrameType] = logging.currentframe()
        depth = 2
        while frame is not None and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """
    Configure logging.

    Effects:
    - Capture warning to logs
    - Enforce third party logs
    """
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    logging.captureWarnings(True)
    logging.root.handlers = [InterceptHandler()]

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.disable("absl")
