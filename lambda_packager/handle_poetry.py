import logging
import subprocess

import toml


class PoetryNotInstalled(Exception):
    pass


def poetry_is_used(current_directory):
    config = _get_poetry_config(current_directory)
    if config is None:
        return False

    try:
        requires = config["build-system"]["requires"][0].startswith("poetry")
        build_backend = config["build-system"]["build-backend"].startswith("poetry")

        return requires and build_backend
    except KeyError:
        return False


def export_poetry(target_path, project_directory=None, env=None):
    if project_directory is not None:
        config = _get_poetry_config(project_directory)
    else:
        config = None

    export_without_hashes = False

    if config is not None:
        try:
            export_without_hashes = config["tool"]["lambda-packager"]["without_hashes"]
        except KeyError:
            pass

    try:
        cmd = [
            "poetry",
            "export",
            "--no-interaction",
            "--verbose",
            "--with-credentials",
            "--format",
            "requirements.txt",
            "--output",
            target_path,
        ]

        if export_without_hashes:
            cmd.append("--without-hashes")

        subprocess.check_output(
            cmd,
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


def _get_poetry_config(current_directory):
    pyproject = current_directory.joinpath("pyproject.toml")
    if not pyproject.is_file():
        return None
    return toml.loads(pyproject.read_text())
