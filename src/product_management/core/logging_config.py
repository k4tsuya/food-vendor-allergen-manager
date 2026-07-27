"""Application logging configuration."""

import logging
import sys

def configure_logging() -> None:
    logging.basicConfig(stream=sys.stdout, 
                        level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S",
                        format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
                        )
