class Config:
    def __init__(
        self,
        src_patterns=None,
        ignore_hidden_files=True,
        ignore_folders=None,
        without_hashes=False,
    ):
        if ignore_folders is None:
            ignore_folders = []

        if src_patterns is None:
            src_patterns = ["*.py"]

        self.ignore_folders = ignore_folders
        self.src_patterns = src_patterns
        self.ignore_hidden_files = ignore_hidden_files
        self.without_hashes = without_hashes
