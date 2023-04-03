import shutil
from pathlib import Path

TEST_PIP_FILE = """pip-install-test==0.5
"""
# the 0.5 version of this test package contains a single file with a print statement


def with_test_poetry_files(test_path):
    config_file = test_path.joinpath("pyproject.toml")
    shutil.copyfile(Path("test/resources/test_project_config.toml"), config_file)
    assert config_file.exists()

    lock_file = test_path.joinpath("poetry.lock")
    shutil.copyfile(Path("test/resources/test_project_config_lockfile"), lock_file)
    assert config_file.exists()

    return config_file


def with_requirements_file(test_path):
    requirements = test_path.joinpath("requirements.txt")
    requirements.write_text(TEST_PIP_FILE)
    return requirements


def with_config_file(test_path, example_file):
    target_file = test_path.joinpath("pyproject.toml")
    shutil.copyfile(example_file, target_file)
    assert target_file.exists()
    return target_file
