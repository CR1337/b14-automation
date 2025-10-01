from abc import ABC
import json
from webapp.app import App
from webapp.app_io import AppIO
from webapp.file_access_mixin import FileAccessMixin
from typing import Any, Dict, List, Tuple, Callable, Type


class AppFactory(ABC, FileAccessMixin):

    CONFIG_FILENAME: str = "config.json"

    _input_validators: Dict[str, Callable[[Any], bool]]
    _output_validators: Dict[str, Callable[[Any], bool]]

    def __init__(self):
        self._input_validators = {}
        self._output_validators = {}

    def config_from_file(self, filename: str) -> Tuple[Dict[str, str], bool, List[AppIO], List[AppIO]]:
        with open(filename, "r", encoding="utf-8") as file:
            config = json.load(file)
        name = config["name"]
        authentication_required = config["authentication_required"]
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
        return name, authentication_required, inputs, outputs

    def create(
        self, 
        app_class: Type[App],
        input_validators: Dict[str, Callable[[Any], bool]] | None = None,
        output_validators: Dict[str, Callable[[Any], bool]] | None = None
    ) -> App:
        self._input_validators = input_validators or {}
        self._output_validators = output_validators or {}
        config_filename = app_class._get_full_filename(self.CONFIG_FILENAME)
        return app_class(*self.config_from_file(config_filename))
