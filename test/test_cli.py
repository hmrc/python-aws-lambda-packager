from lambda_packager import parse_args


def test_cli_no_args():
    parsed = parse_args([])
    assert parsed
    assert parsed.project_directory is None
    assert parsed.log_level == "INFO"


def test_cli_with_optional_args():
    parsed = parse_args(["-l", "WARNING"])
    assert parsed
    assert parsed.log_level == "WARNING"


def test_cli_with_long_args():
    parsed = parse_args(["--log-level", "WARNING", "--project-directory", "test"])
    assert parsed
    assert parsed.project_directory == "test"
    assert parsed.log_level == "WARNING"
