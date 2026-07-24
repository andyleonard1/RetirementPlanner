"""
Logging configuration
"""

import logging


def setup_logging():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler("RetirementPlanner.log"),
            logging.StreamHandler(),
        ],
    )