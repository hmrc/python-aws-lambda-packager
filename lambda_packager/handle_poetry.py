import logging
import subprocess

import toml


class PoetryNotInstalled(Exception):
    pass


def poetry_is_used(current_directory):
    pyproject = current_directory.joinpath("pyproject.toml")
    if not pyproject.is_file():
        return False
    config = toml.loads(pyproject.read_text())

    try:
        requires = config["build-system"]["requires"][0].startswith("poetry")
        build_backend = config["build-system"]["build-backend"].startswith("poetry")

        return requires and build_backend
    except KeyError:
        return False


def export_poetry(target_path, project_directory=None, env=None):
    try:
        subprocess.check_output(
            [
                "poetry",
                "export",
                "--no-interaction",
                "--verbose",
                "--with-credentials",
                "--format",
                "requirements.txt",
                "--output",
                target_path,
            ],
            env=env,
            cwd=project_directory,
        )
    except FileNotFoundError as e:
        raise PoetryNotInstalled(
            "Please make sure you have poetry installed and in your path", e
        )
    except subprocess.CalledProcessError as e:
        logging.error(e.stdout.decode())
        raise e
