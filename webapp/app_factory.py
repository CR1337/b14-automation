from abc import ABC, abstractmethod
import json
from webapp.app import App
from webapp.app_io import AppIO
from webapp.file_access_mixin import FileAccessMixin
from typing import Any, Dict, List, Tuple, Callable


class AppFactory(ABC, FileAccessMixin):

    CONFIG_FILENAME: str = "config.json"

    _input_validators: Dict[str, Callable[[Any], bool]]
    _output_validators: Dict[str, Callable[[Any], bool]]

    def __init__(self):
        self._input_validators = {}
        self._output_validators = {}

    def config_from_file(self) -> Tuple[Dict[str, str], List[AppIO], List[AppIO]]:
        filename = self._get_full_filename(self.CONFIG_FILENAME)
        with open(filename, "r", encoding="utf-8") as file:
            config = json.load(file)
        name = config["name"]
        inputs = config["inputs"]
        outputs = config["outputs"]
        for i in inputs:
            i["type"] = AppIO.TYPE_NAMES[i["type"]]
            i["validator"] = self._input_validators.get(i["key"], lambda _: True)
        for o in outputs:
            o["type"] = AppIO.TYPE_NAMES[o["type"]]
            o["validator"] = self._output_validators.get(o["key"], lambda _: True)
        inputs = [AppIO.make_input(**i) for i in inputs]
        outputs = [AppIO.make_output(**o) for o in outputs]
        return name, inputs, outputs

    @abstractmethod
    def create(self) -> App:
        raise NotImplementedError("@abstractmethod")
    
    def add_input_validator(self, key: str, validator: Callable[[Any], bool]):
        self._input_validators[key] = validator

    def add_output_validator(self, key: str, validator: Callable[[Any], bool]):
        self._output_validators[key] = validator
