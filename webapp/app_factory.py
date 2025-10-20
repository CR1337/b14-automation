from abc import ABC
import json
from webapp.app import App
from webapp.app_io.app_io import AppIO
from webapp.app_configuration import AppConfiguration
from webapp.file_access_mixin import FileAccessMixin
from typing import Any, Dict, Callable, Type


class AppFactory(ABC, FileAccessMixin):

    CONFIG_FILENAME: str = "config.json"

    _input_validators: Dict[str, Callable[[Any], bool]]
    _output_validators: Dict[str, Callable[[Any], bool]]

    @staticmethod
    def _construct_key(key: str, app_name: str, is_input: bool) -> str:
        return f"{key}_{app_name.replace(' ', '_')}_{'input' if is_input else 'output'}"

    def __init__(self):
        self._input_validators = {}
        self._output_validators = {}

    def config_from_file(
        self, 
        filename: str
    ) -> AppConfiguration:
        with open(filename, "r", encoding="utf-8") as file:
            config = json.load(file)
        name = config["name"]
        authentication_required = config["authentication_required"]
        inputs = config["inputs"]
        outputs = config["outputs"]
        input_key_mappings = {i['key']: self._construct_key(i['key'], name['en'], True) for i in inputs}
        output_key_mappings = {o['key']: self._construct_key(o['key'], name['en'], False) for o in outputs}
        for io_set in (inputs, outputs):
            for io in io_set:
                io["type"] = AppIO.TYPE_NAMES[io["type"]]
                io["validator"] = self._input_validators.get(io["key"], lambda _: True)
                io["key"] = self._construct_key(io["key"], name["en"], io_set is inputs)
                io["type_"] = io["type"]
                del io["type"]
        inputs = [AppIO.make_input(**i) for i in inputs]
        outputs = [AppIO.make_output(**o) for o in outputs]
        return AppConfiguration(name, authentication_required, inputs, outputs, input_key_mappings, output_key_mappings)

    def create(
        self, 
        app_class: Type[App],
        input_validators: Dict[str, Callable[[Any], bool]] | None = None,
        output_validators: Dict[str, Callable[[Any], bool]] | None = None
    ) -> App:
        self._input_validators = input_validators or {}
        self._output_validators = output_validators or {}
        config_filename = app_class._get_full_filename(self.CONFIG_FILENAME)
        return app_class(*self.config_from_file(config_filename).to_tuple())
