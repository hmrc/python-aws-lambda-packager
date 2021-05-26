import pytest

from lambda_packager import LambdaAutoPackage
from lambda_packager.poetry import export_poetry, PoetryNotInstalled, poetry_is_used

EXAMPLE_PYPROJECT = """
[tool.poetry]
name = "EXAMPLE_PYPROJECT"
version = "0.1.0"
description = "EXAMPLE_PYPROJECT"
authors = ["EXAMPLE_PYPROJECT"]

[tool.poetry.dependencies]
pip-install-test = "^0.5"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
"""

BROKEN_PYPROJECT = """
[build-system]
requires = "foo"
"""


def with_poetry_toml_file(test_path):
    pyproject = test_path.joinpath("pyproject.toml")
    pyproject.write_text(EXAMPLE_PYPROJECT)
    return pyproject


def test_poetry_is_not_used():
    test_path = LambdaAutoPackage._create_tmp_directory()
    assert not poetry_is_used(current_directory=test_path)


def test_poetry_checks_for_build_system():
    test_path = LambdaAutoPackage._create_tmp_directory()

    pyproject = test_path.joinpath("pyproject.toml")
    pyproject.write_text("")

    assert not poetry_is_used(current_directory=test_path)


def test_poetry_checks_for_build_system_wrong_format():
    test_path = LambdaAutoPackage._create_tmp_directory()

    pyproject = test_path.joinpath("pyproject.toml")
    pyproject.write_text(BROKEN_PYPROJECT)

    assert not poetry_is_used(current_directory=test_path)


def test_poetry_is_used():
    test_path = LambdaAutoPackage._create_tmp_directory()
    with_poetry_toml_file(test_path)

    assert poetry_is_used(current_directory=test_path)


def test_export_poetry():
    test_path = LambdaAutoPackage._create_tmp_directory()
    with_poetry_toml_file(test_path)

    expected_path = test_path.joinpath("requirements.txt")

    assert poetry_is_used(current_directory=test_path)

    export_poetry(
        target_path=str(expected_path), project_directory=str(test_path.resolve())
    )

    assert expected_path.exists()
    output = expected_path.read_text()
    assert "pip-install-test" in output
    assert "--hash=sha256" in output


def test_export_poetry_fails_if_no_exec_found():
    test_path = LambdaAutoPackage._create_tmp_directory()
    expected_path = test_path.joinpath("requirements.txt")

    with pytest.raises(
        PoetryNotInstalled,
        match=r"Please make sure you have poetry installed and in your path*",
    ):
        export_poetry(str(expected_path), env={})
