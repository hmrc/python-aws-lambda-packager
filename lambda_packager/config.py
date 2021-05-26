class Config:
    def __init__(self, src_patterns=None, ignore_hidden_files=True):
        if src_patterns is None:
            src_patterns = ["*.py"]

        self.src_patterns = src_patterns
        self.ignore_hidden_files = ignore_hidden_files
