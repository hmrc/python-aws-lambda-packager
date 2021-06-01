import logging
import subprocess
import sys
from pathlib import Path


def install_requirements_txt(target, requirements_file_path: Path, no_deps=False):
    # https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program
    if not requirements_file_path.is_file():
        raise ValueError(
            f"could not find requirements.txt file at '{requirements_file_path}'"
        )

    logging.info(f"installing pip requirements to '{target}'")
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        requirements_file_path,
        "--target",
        target,
    ]
    if no_deps:
        cmd.append("--no-deps")

    output = subprocess.check_output(cmd)
    logging.debug(output.decode())
    return output
