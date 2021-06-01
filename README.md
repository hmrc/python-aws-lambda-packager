# lambda-packager

Currently, requires python >=3.8 and later due to [required features of copytree](https://docs.python.org/3/library/shutil.html#shutil.copytree)

##Usage
- Just run the packager with:
```bash
$ lambda-packager
 # or if not in the project directory  
$ lambda-packager path/to/project/dir
```
- lambda-packager will include any dependencies defined in
    - poetry (pyproject.toml)
    - requirements.txt
    - ~~Pipenv~~ (Coming soon!)
- By default lambda-packager will include all src files that match `*.py`
- You can customise this with the following config:
```toml
[tool.lambda-packager]
src_patterns = ["lambda_packager/*.py"]
```

### Hidden files
- hidden files and folders are ignored by default when including src files
- if you wish to disable this then add the following config to you pyproject.toml
```toml
[tool.lambda-packager]
ignore_hidden_files = false
```

### Ignore folders
If there are folders that you wish always exclude then you can use `ignore_folders`
Note: `ignore_folders` is always respected even if there was a match via `src_patterns`
```toml
[tool.lambda-packager]
ignore_folders = ["venv"]
```

## License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
