"""Application logging configuration."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def configure_logging() -> None:
    os.makedirs("logs", exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d | %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=5),
        ],
    )