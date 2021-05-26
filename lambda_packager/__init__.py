import logging
import sys
from pathlib import Path

from lambda_packager.custom_log_formatter import CustomLogFormatter
from lambda_packager.package import LambdaAutoPackage


def run_cli():
    log_level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(log_level)

    ch = logging.StreamHandler()
    ch.setFormatter(CustomLogFormatter())
    ch.setLevel(log_level)
    logger.addHandler(ch)

    if len(sys.argv) > 1:
        project_directory = Path(sys.argv[1])
        assert project_directory.exists()
    else:
        project_directory = Path()

    LambdaAutoPackage(logger=logger, project_directory=project_directory).execute()
