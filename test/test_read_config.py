from pathlib import Path

from lambda_packager.package import LambdaAutoPackage


def test_read_toml_file():
    test_file = Path("test/resources/test_full_config.toml")
    assert test_file.exists()

    response = LambdaAutoPackage._get_config(test_file.absolute())
    assert response.src_patterns == ["lambda_packager", "test_file_*"]
    assert not response.ignore_hidden_files
    assert response.without_hashes


def test_read_toml_file_when_missing():
    test_file = Path("fake_file_name")
    assert not test_file.exists()

    response = LambdaAutoPackage._get_config(test_file.absolute())
    assert response.src_patterns == ["*.py"]
    assert response.ignore_hidden_files


def test_read_toml_file_when_no_config_in_file():
    test_file = Path("test/resources/config_we_do_not_care_about.toml")
    assert test_file.exists()

    response = LambdaAutoPackage._get_config(test_file.absolute())
    assert response.src_patterns == ["*.py"]
    assert response.ignore_hidden_files
