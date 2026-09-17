import logging
import sys
from typing import Any, Dict


def setup_logging() -> logging.Logger:
    """Configure structured logging for AI PlacementOS."""
    logger = logging.getLogger("placement_os")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
