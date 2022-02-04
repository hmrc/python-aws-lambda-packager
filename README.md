# lambda-packager

<a href="https://github.com/hmrc"><img alt="HMRC: Digital" src="https://img.shields.io/badge/HMRC-Digital-FFA500?style=flat&labelColor=000000&logo=gov.uk"></a>
<a href="https://pypi.org/project/lambda-packager/"><img alt="PyPI" src="https://img.shields.io/pypi/v/lambda-packager"></a>
<a href="https://pypi.org/project/lambda-packager/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/lambda-packager"></a>
<a href="https://github.com/hmrc/python-aws-lambda-packager/blob/master/LICENSE"><img alt="License: Apache 2.0" src="https://img.shields.io/github/license/hmrc/python-aws-lambda-packager"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

The purpose of this tool is to avoid writing AWS lambda packaging scripts repeatedly. It is intended to give a consistent output regardless of how you currently define your python dependencies. The tool was built as most existing tools are built into larger frameworks that have other considerations when adopting

Currently, requires python >=3.8 and later due to [required features of copytree](https://docs.python.org/3/library/shutil.html#shutil.copytree)

## Usage
- You can run with the following:
```bash
$ lambda-packager
 # or if not in the project directory  
$ lambda-packager --project-directory path/to/project/dir
```
- lambda-packager will include any dependencies defined in
    - poetry (pyproject.toml)
    - requirements.txt
    - ~~Pipenv~~ (Coming soon!)
- By default lambda-packager will include all src files that match `*.py`
- You can customise this through config in `pyproject.toml`:
```toml
[tool.lambda-packager]
src_patterns = ["lambda_packager/*.py"]
```

### Hidden files
- Hidden files and folders are ignored by default when including src files
- if you wish to disable this, then add the following config to your `pyproject.toml`
```toml
[tool.lambda-packager]
ignore_hidden_files = false
```

### Ignore folders
If there are folders that you wish always exclude, then you can use `ignore_folders`
Note: `ignore_folders` is always respected even if there was a match via `src_patterns`
```toml
[tool.lambda-packager]
ignore_folders = ["venv"]
```

### Ignore hashes
Only has an effect when using poetry `pyproject.toml` files

Skips exporting hashes from poetry to avoid issues when using non-pypi packages 
by providing `--without-hashes` flag when calling `poetry export`
See https://github.com/hmrc/python-aws-lambda-packager/issues/2 for more info (Note: version number remains pinned when this is enabled)
```toml
without_hashes = True
```

### Full usage
```
usage: lambda-packager [-h] [--project-directory PROJECT_DIRECTORY] [-l {DEBUG,INFO,WARNING,ERROR}]

Build code and dependencies into zip files that can be uploaded and run in AWS Lambda

optional arguments:
  -h, --help            show this help message and exit
  --project-directory PROJECT_DIRECTORY
                        The path to the top level project directory. This is where source files and files that declare dependencies are expected to be held. Defaults to current directory
  -l {DEBUG,INFO,WARNING,ERROR}, --log-level {DEBUG,INFO,WARNING,ERROR}
                        set output verbosity, defaults to 'INFO'

```

## License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
