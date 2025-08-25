import os
import inspect


class FileAccessMixin:

    @classmethod
    def _get_full_filename(cls, filename: str) -> str:
        source_filename = os.path.abspath(inspect.getfile(cls))
        source_directory = os.path.dirname(source_filename)
        return os.path.join(source_directory, filename)
    