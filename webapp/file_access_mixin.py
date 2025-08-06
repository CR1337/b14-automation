import os
import inspect


class FileAccessMixin:

    def _get_full_filename(self, filename: str) -> str:
        cls = self.__class__
        source_filename = os.path.abspath(inspect.getfile(cls))
        source_directory = os.path.dirname(source_filename)
        return os.path.join(source_directory, filename)
    