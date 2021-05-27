import logging
import unittest
import shutil
import zipfile
from pathlib import Path

import pytest

from lambda_packager.config import Config
from lambda_packager.handle_requirements_txt import install_requirements_txt
from lambda_packager.package import LambdaAutoPackage
import test_file_helpers


def test_build_lambda_with_no_dependency(caplog):
    test_path = LambdaAutoPackage._create_tmp_directory()

    file1 = test_path.joinpath("test_file_1.py")
    file1.write_text("test file 1")

    file2 = test_path.joinpath("not_this_file")
    file2.write_text("not_this_file")

    with caplog.at_level(logging.INFO):
        LambdaAutoPackage(project_directory=test_path).execute()

    assert "No dependency found, none will be packaged" in caplog.text

    actual_zip = test_path.joinpath("dist/lambda.zip")
    assert actual_zip.is_file()

    zip = zipfile.ZipFile(actual_zip)
    assert ["test_file_1.py"] == zip.namelist()


def test_build_lambda_with_requirements_txt(caplog):
    test_path = LambdaAutoPackage._create_tmp_directory()

    test_file_helpers.with_requirements_file(test_path)
    test_config = Path("test/resources/test_config.toml")
    test_file_helpers.with_config_file(test_path, test_config)

    file1 = test_path.joinpath("test_file_1")
    file1.write_text("test file 1")

    file2 = test_path.joinpath("not_this_file")
    file2.write_text("not_this_file")

    with caplog.at_level(logging.INFO):
        LambdaAutoPackage(project_directory=test_path).execute()

    assert "using requirements.txt file in project directory" in caplog.text

    actual_zip = test_path.joinpath("dist/lambda.zip")
    assert actual_zip.is_file()

    zip = zipfile.ZipFile(actual_zip)
    assert "test_file_1" in zip.namelist()
    assert "not_this_file" not in zip.namelist()


def test_build_lambda_with_pyproject_toml(caplog):
    test_path = LambdaAutoPackage._create_tmp_directory()
    test_file_helpers.with_poetry_toml_file(test_path)

    file1 = test_path.joinpath("test_file_1.py")
    file1.write_text("test file 1")

    file2 = test_path.joinpath("not_this_file.md")
    file2.write_text("not_this_file")

    with caplog.at_level(logging.INFO):
        LambdaAutoPackage(project_directory=test_path).execute()

    assert "using pyproject.toml file in project directory" in caplog.text

    actual_zip = test_path.joinpath("dist/lambda.zip")
    assert actual_zip.is_file()

    zip = zipfile.ZipFile(actual_zip)
    assert "test_file_1.py" in zip.namelist()
    assert "not_this_file.md" not in zip.namelist()


def test_error_when_no_requirements_text_is_installed():
    test_path = LambdaAutoPackage._create_tmp_directory()
    requirements = test_path.joinpath("requirements.txt")
    target = test_path.joinpath("dist")

    with pytest.raises(
        ValueError,
        match=f"could not find requirements.txt file*",
    ):
        install_requirements_txt(
            requirements_file_path=requirements,
            target=str(target),
        )


def test_requirements_txt_is_installed():
    test_path = LambdaAutoPackage._create_tmp_directory()
    requirements = test_file_helpers.with_requirements_file(test_path)
    target = test_path.joinpath("dist")

    install_requirements_txt(
        requirements_file_path=requirements,
        target=str(target),
    )

    assert target.is_dir()
    assert target.joinpath("pip_install_test/__init__.py").is_file()


def test_create_incorrect_extension():
    test_path = LambdaAutoPackage._create_tmp_directory()
    file1 = test_path.joinpath("test_file_1")
    file1.write_text("test file 1")

    expected_file_path = test_path.joinpath("lambda.tar.gz")

    with pytest.raises(
        ValueError,
        match=f"given target path '{expected_file_path}' does not end with correct extension. should end with '.zip'",
    ):
        LambdaAutoPackage._create_zip_file(
            source_dir=str(test_path),
            target=str(expected_file_path),
        )


def test_create_zipfile():
    test_path = LambdaAutoPackage._create_tmp_directory()
    file1 = test_path.joinpath("test_file_1")
    file1.write_text("test file 1")
    file2 = test_path.joinpath("a_folder/test_file_2")
    file2.parent.mkdir()
    file2.write_text("test file 2")

    expected_file_path = test_path.joinpath("lambda.zip")
    LambdaAutoPackage._create_zip_file(
        source_dir=str(test_path),
        target=str(expected_file_path),
    )

    assert expected_file_path.exists()
    assert expected_file_path.is_file()


def test_copy_source_files():
    test_path = LambdaAutoPackage._create_tmp_directory()
    source_dir = LambdaAutoPackage._create_tmp_directory()
    file1 = source_dir.joinpath("test_file_1")
    file1.write_text("test file 1")
    file2 = source_dir.joinpath("a_folder/test_file_2")
    file2.parent.mkdir()
    file2.write_text("test file 2")

    file3 = source_dir.joinpath("a_folder_2/other_file")
    file3.parent.mkdir()
    file3.write_text("test file 2")

    LambdaAutoPackage(
        config=Config(src_patterns=["test_file_*", "a_folder_2"])
    )._copy_source_files(
        source_dir=source_dir,
        target_dir=test_path,
    )

    assert test_path.joinpath("test_file_1").exists()
    assert test_path.joinpath("a_folder/test_file_2").exists()
    assert test_path.joinpath("a_folder_2/other_file").exists()


def test_copy_source_files_ignores_hidden_files():
    test_path = LambdaAutoPackage._create_tmp_directory()
    source_dir = LambdaAutoPackage._create_tmp_directory()
    file1 = source_dir.joinpath("test_file_1")
    file1.write_text("test file 1")

    file2 = source_dir.joinpath(".dotfolder/test_file_2")
    file2.parent.mkdir()
    file2.write_text("test file 2")

    file3 = source_dir.joinpath("a_folder_2/.dotfile")
    file3.parent.mkdir()
    file3.write_text("test file 2")

    file3 = source_dir.joinpath("a_folder_3/.dotfile-2")
    file3.parent.mkdir()
    file3.write_text("test file 2")

    file3 = source_dir.joinpath(
        "terraform/.terraform/modules/label-proxy-lambda/test/src"
    )
    file3.parent.mkdir(parents=True)
    file3.write_text("test file 2")

    LambdaAutoPackage(
        config=Config(
            src_patterns=[
                "src",
                "test_file_*",
                "a_folder_2",
                ".dotfile-2",
                ".dotfolder",
            ]
        )
    )._copy_source_files(
        source_dir=source_dir,
        target_dir=test_path,
    )

    assert test_path.joinpath("test_file_1").exists()

    assert not test_path.joinpath("a_folder_2/.dotfile").exists()
    assert not test_path.joinpath(".dotfolder/test_file_2").exists()
    assert not test_path.joinpath("a_folder_3/.dotfile-2").exists()

    assert not test_path.joinpath("terraform").is_dir()
    assert not test_path.joinpath(
        "terraform/.terraform/modules/label-proxy-lambda/test/a_folder_2"
    ).exists()


def test_copy_source_files_includes_hidden_files_when_asked():
    test_path = LambdaAutoPackage._create_tmp_directory()
    source_dir = LambdaAutoPackage._create_tmp_directory()
    file1 = source_dir.joinpath("test_file_1")
    file1.write_text("test file 1")

    file2 = source_dir.joinpath(".dotfolder/test_file_2")
    file2.parent.mkdir()
    file2.write_text("test file 2")

    file3 = source_dir.joinpath("a_folder_2/.dotfile")
    file3.parent.mkdir()
    file3.write_text("test file 2")

    file3 = source_dir.joinpath("a_folder_3/.dotfile-2")
    file3.parent.mkdir()
    file3.write_text("test file 2")

    LambdaAutoPackage(
        config=Config(ignore_hidden_files=False, src_patterns=["*"])
    )._copy_source_files(
        source_dir=source_dir,
        target_dir=test_path,
    )
    assert test_path.joinpath("test_file_1").exists()
    assert test_path.joinpath("a_folder_2/.dotfile").exists()
    assert test_path.joinpath(".dotfolder/test_file_2").exists()
    assert test_path.joinpath("a_folder_3/.dotfile-2").exists()


def test_copy_source_files_follows_symlinks():
    test_path = LambdaAutoPackage._create_tmp_directory()
    source_dir = LambdaAutoPackage._create_tmp_directory()
    file = source_dir.joinpath("real_file")
    file.write_text("test file 2")

    simlink_file = source_dir.joinpath("simlink_file")
    simlink_file.symlink_to(file)

    LambdaAutoPackage(config=Config(src_patterns=["simlink_file"]))._copy_source_files(
        source_dir=source_dir,
        target_dir=test_path,
    )

    assert test_path.joinpath("simlink_file").exists()

    assert not test_path.joinpath("simlink_file").is_symlink()
    assert not test_path.joinpath("real_file").exists()
