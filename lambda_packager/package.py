import logging
import shutil
import tempfile
from pathlib import Path

import toml

from lambda_packager.config import Config
from lambda_packager.handle_poetry import poetry_is_used, export_poetry
from lambda_packager.handle_requirements_txt import install_requirements_txt


class NoSrcFilesFound(Exception):
    pass


class LambdaAutoPackage:
    def __init__(self, config=None, project_directory=None, logger=None):
        if project_directory:
            self.project_directory = Path(project_directory)
        else:
            self.project_directory = Path()

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.debug("set up self logging")

        if config:
            self.config = config
        else:
            self.config = LambdaAutoPackage._get_config(
                self.project_directory.joinpath("pyproject.toml")
            )

        self.tmp_folder = self._create_tmp_directory()

    def execute(self):

        if self.project_directory.joinpath("requirements.txt").is_file():
            self.logger.info("using requirements.txt file in project directory")
            requirements_file_path = self.project_directory.joinpath("requirements.txt")
            install_requirements_txt(
                str(self.tmp_folder), requirements_file_path=requirements_file_path
            )
        elif poetry_is_used(self.project_directory):
            self.logger.info("using pyproject.toml file in project directory")
            requirements_file_path = self.tmp_folder.joinpath("requirements.txt")
            export_poetry(
                target_path=requirements_file_path,
                project_directory=self.project_directory,
                without_hashes=self.config.without_hashes,
            )
            install_requirements_txt(
                str(self.tmp_folder),
                requirements_file_path=requirements_file_path,
                no_deps=True,
            )
        else:
            self.logger.warning("No dependency found, none will be packaged")

        self._copy_source_files(
            source_dir=self.project_directory,
            target_dir=self.tmp_folder,
        )

        self._create_zip_file(
            self.tmp_folder, str(self.project_directory.joinpath("dist/lambda.zip"))
        )

    @staticmethod
    def _create_tmp_directory():
        dirpath = tempfile.mkdtemp()
        test_path = Path(dirpath)
        assert test_path.exists()
        assert test_path.is_dir()
        return test_path

    def _copy_source_files(self, source_dir: Path, target_dir: Path):
        matching_objects = LambdaAutoPackage._get_matching_files_and_folders(
            self.config.src_patterns, source_dir
        )

        self.logger.info(f"copying {len(matching_objects)} matching_objects")
        self.logger.debug(f"copying {matching_objects} matching_objects")

        copied_locations = []
        for src in matching_objects:
            relative_path = src.relative_to(source_dir)
            new_location = target_dir.joinpath(relative_path)

            if self._is_ignored_file(src.resolve()):
                self.logger.warning(f"skipping path {src.resolve()}")
            elif src.is_file():
                self.copy_file(src, new_location, copied_locations)
            elif src.is_dir():
                self.copy_directory(src, new_location, copied_locations)
            else:
                self.logger.warning(f"the path '{src}' was nether a file or directory")

        if len(copied_locations) <= 0:
            raise NoSrcFilesFound(
                "No src files were found. This is likely a problem. Exiting now to highlight this"
            )

        copied_locations_string = "\n".join(copied_locations)
        self.logger.info(f"copied the following locations: \n{copied_locations_string}")

    def copy_file(self, src, new_location, copied_locations):
        self.logger.debug(f"about to copy file from {src} --> {new_location}")
        new_location.parent.mkdir(exist_ok=True, parents=True)
        copied_locations.append(str(shutil.copyfile(src, new_location)))

    def copy_directory(self, src, new_location, copied_locations):
        self.logger.debug(f"about to copy directory from {src} --> {new_location}")
        copied_locations.append(
            str(
                shutil.copytree(
                    src=str(src),
                    dst=str(new_location),
                    dirs_exist_ok=True,
                    ignore=(
                        self._is_ignored_file_list
                        if self.config.ignore_hidden_files or self.config.ignore_folders
                        else None
                    ),
                )
            )
        )

    def _is_ignored_file_list(self, src, files):
        if self._is_ignored_file(Path(src).resolve()):
            self.logger.warning(f"skipping folder {Path(src).resolve()}")
            return files

        files_to_skip = {}
        for file in files:
            path = Path(file).resolve()
            if self._is_ignored_file(path):
                files_to_skip[file] = path

        if files_to_skip:
            self.logger.warning(f"skipping path {list(files_to_skip.values())}")
        return files_to_skip.keys()

    def _is_ignored_file(self, resolved_path: Path):
        path = str(resolved_path)

        if self.config.ignore_hidden_files:
            if path.startswith(".") or "/." in path:
                return True

        for folder in self.config.ignore_folders:
            if f"/{folder}" in path:
                return True

        return False

    @staticmethod
    def _get_matching_files_and_folders(pattern_list, source_dir):
        matching_objects = set()
        for pattern in pattern_list:
            matching_objects.update(source_dir.rglob(pattern))

        return matching_objects

    @staticmethod
    def _create_zip_file(source_dir, target):
        if target.endswith(".zip"):
            Path(target).parent.mkdir(exist_ok=True)
            name = target[: -len(".zip")]
            shutil.make_archive(base_name=name, format="zip", root_dir=source_dir)
        else:
            raise ValueError(
                f"given target path '{target}' does not end with correct extension. should end with '.zip'"
            )

    @staticmethod
    def _read_config(file: Path):
        config = toml.loads(file.read_text())

        try:
            return config["tool"]["lambda-packager"]
        except KeyError:
            logging.warning("no config found!")
            return {}

    @staticmethod
    def _get_config(file: Path):
        if not file.is_file():
            logging.warning("no config file found!")
            return Config()

        config_dict = LambdaAutoPackage._read_config(file)
        return Config(**config_dict)
