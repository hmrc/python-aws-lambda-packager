import argparse
import logging
import sys
from pathlib import Path

from lambda_packager.custom_log_formatter import CustomLogFormatter
from lambda_packager.package import LambdaAutoPackage


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Build code and dependencies into zip files that can be uploaded and run in AWS Lambda"
    )
    parser.add_argument(
        "--project-directory",
        dest="project_directory",
        required=False,
        default=None,
        help="""The path to the top level project directory.
                This is where source files and files that declare dependencies are expected to be held.
                Defaults to current directory""",
    )
    logging_default = logging.getLevelName(logging.INFO)
    parser.add_argument(
        "-l",
        "--log-level",
        dest="log_level",
        required=False,
        default=logging_default,
        help=f"set output verbosity, defaults to '{logging_default}'",
        choices=[
            logging.getLevelName(logging.DEBUG),
            logging.getLevelName(logging.INFO),
            logging.getLevelName(logging.WARNING),
            logging.getLevelName(logging.ERROR),
        ],
    )
    return parser.parse_args(args)


def run_cli():
    args = parse_args(sys.argv[1:])

    if args.project_directory:
        project_directory = Path(args.project_directory)
        assert project_directory.exists()
    else:
        project_directory = Path()

    log_level = logging.getLevelName(args.log_level)
    logger = logging.getLogger()
    logger.setLevel(log_level)

    ch = logging.StreamHandler()
    ch.setFormatter(CustomLogFormatter())
    ch.setLevel(log_level)
    logger.addHandler(ch)

    try:
        LambdaAutoPackage(logger=logger, project_directory=project_directory).execute()
    except Exception as e:
        logger.critical(e)
        raise e
