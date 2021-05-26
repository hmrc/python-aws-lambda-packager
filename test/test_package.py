import unittest
import shutil
import zipfile
from pathlib import Path

from lambda_packager.package import LambdaAutoPackage, Config

TEST_PIP_FILE = """pip-install-test==0.5
"""
# the 0.5 version of this test package contains a single file with a print statement


class TestPackageUnit(unittest.TestCase):
    def setUp(self):
        self._test_path = LambdaAutoPackage._create_tmp_directory()

    def tearDown(self):
        shutil.rmtree(self._test_path)

    def with_requirements_file(self):
        requirements = self._test_path.joinpath("requirements.txt")
        requirements.write_text(TEST_PIP_FILE)
        return requirements

    def with_config_file(self, example_file):
        target_file = self._test_path.joinpath("pyproject.toml")
        shutil.copyfile(example_file, target_file)
        assert target_file.exists()
        return target_file

    def test_build_lambda_functions_correctly(self):
        self.with_requirements_file()
        test_config = Path("test/resources/test_config.toml")
        self.with_config_file(test_config)

        file1 = self._test_path.joinpath("test_file_1")
        file1.write_text("test file 1")

        file2 = self._test_path.joinpath("not_this_file")
        file2.write_text("not_this_file")

        LambdaAutoPackage(project_directory=self._test_path).execute()

        actual_zip = self._test_path.joinpath("dist/lambda.zip")
        self.assertTrue(actual_zip.is_file())

        zip = zipfile.ZipFile(actual_zip)
        assert "test_file_1" in zip.namelist()
        assert "not_this_file" not in zip.namelist()

    def test_error_when_no_requirements_text_is_installed(self):
        requirements = self._test_path.joinpath("requirements.txt")
        target = self._test_path.joinpath("dist")

        with self.assertRaises(ValueError) as context:
            LambdaAutoPackage._install_requirements_txt(
                requirements_file_path=requirements,
                target=str(target),
            )
        self.assertIn("could not find requirements.txt file", str(context.exception))

    def test_requirements_txt_is_installed(self):
        requirements = self.with_requirements_file()
        target = self._test_path.joinpath("dist")

        LambdaAutoPackage._install_requirements_txt(
            requirements_file_path=requirements,
            target=str(target),
        )

        self.assertTrue(target.is_dir())
        self.assertTrue(target.joinpath("pip_install_test/__init__.py").is_file())

    def test_create_incorrect_extension(self):
        file1 = self._test_path.joinpath("test_file_1")
        file1.write_text("test file 1")

        expected_file_path = self._test_path.joinpath("lambda.tar.gz")
        with self.assertRaises(ValueError) as context:
            LambdaAutoPackage._create_zip_file(
                source_dir=str(self._test_path),
                target=str(expected_file_path),
            )
        self.assertEqual(
            f"given target path '{expected_file_path}' does not end with correct extension. should end with '.zip'",
            str(context.exception),
        )

    def test_create_zipfile(self):
        file1 = self._test_path.joinpath("test_file_1")
        file1.write_text("test file 1")
        file2 = self._test_path.joinpath("a_folder/test_file_2")
        file2.parent.mkdir()
        file2.write_text("test file 2")

        expected_file_path = self._test_path.joinpath("lambda.zip")
        LambdaAutoPackage._create_zip_file(
            source_dir=str(self._test_path),
            target=str(expected_file_path),
        )

        self.assertTrue(expected_file_path.exists())
        self.assertTrue(expected_file_path.is_file())

    def test_copy_source_files(self):
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
            target_dir=self._test_path,
        )

        self.assertTrue(self._test_path.joinpath("test_file_1").exists())
        self.assertTrue(self._test_path.joinpath("a_folder/test_file_2").exists())
        self.assertTrue(self._test_path.joinpath("a_folder_2/other_file").exists())

    def test_copy_source_files_ignores_hidden_files(self):
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
            config=Config(
                src_patterns=["test_file_*", "a_folder_2", ".dotfile-2", ".dotfolder"]
            )
        )._copy_source_files(
            source_dir=source_dir,
            target_dir=self._test_path,
        )

        self.assertTrue(self._test_path.joinpath("test_file_1").exists())

        self.assertFalse(self._test_path.joinpath("a_folder_2/.dotfile").exists())
        self.assertFalse(self._test_path.joinpath(".dotfolder/test_file_2").exists())
        self.assertFalse(self._test_path.joinpath("a_folder_3/.dotfile-2").exists())

    def test_copy_source_files_includes_hidden_files_when_asked(self):
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
            target_dir=self._test_path,
        )
        self.assertTrue(self._test_path.joinpath("test_file_1").exists())
        self.assertTrue(self._test_path.joinpath("a_folder_2/.dotfile").exists())
        self.assertTrue(self._test_path.joinpath(".dotfolder/test_file_2").exists())
        self.assertTrue(self._test_path.joinpath("a_folder_3/.dotfile-2").exists())

    def test_copy_source_files_follows_symlinks(self):
        source_dir = LambdaAutoPackage._create_tmp_directory()
        file = source_dir.joinpath("real_file")
        file.write_text("test file 2")

        simlink_file = source_dir.joinpath("simlink_file")
        simlink_file.symlink_to(file)

        LambdaAutoPackage(
            config=Config(src_patterns=["simlink_file"])
        )._copy_source_files(
            source_dir=source_dir,
            target_dir=self._test_path,
        )

        self.assertTrue(self._test_path.joinpath("simlink_file").exists())

        self.assertFalse(self._test_path.joinpath("simlink_file").is_symlink())
        self.assertFalse(self._test_path.joinpath("real_file").exists())


if __name__ == "__main__":
    unittest.main()
