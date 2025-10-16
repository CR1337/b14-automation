import os
import inspect
from webapp.app_io.app_io import AppIO
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Tuple
from webapp.app_messenger import AppMessenger
from webapp.file_access_mixin import FileAccessMixin
from webapp.localization import Localization
from functools import cached_property


class App(ABC, FileAccessMixin):

    _inputs: Dict[str, AppIO]
    _outputs: Dict[str, AppIO]
    _name: Dict[str, str]
    _authentication_required: bool
    
    localization: Localization
    messenger: AppMessenger | None

    @cached_property
    def localization_filename(self) -> str:
        script_filename = inspect.getfile(type(self))
        directory = os.path.dirname(script_filename)
        return os.path.join(directory, "localization.json")

    @property
    def name(self) -> Dict[str, str]:
        return self._name
    
    @property
    def authentication_required(self) -> bool:
        return self._authentication_required
    
    @property
    def key(self) -> str:
        return list(self.name.values())[0].lower().strip().replace(" ", "_")
    
    @property
    def inputs(self) -> List[AppIO]:
        return [x for x in self._inputs.values()]
    
    @property
    def outputs(self) -> List[AppIO]:
        return [x for x in self._outputs.values()]
    
    def __repr__(self) -> str:
        return f"App({self._name=}, {self.key=}, {len(self._inputs)=}, {len(self._outputs)=}"

    def __init__(self, name: Dict[str, str], authentication_required: bool, inputs: List[AppIO], outputs: List[AppIO]):
        self._name = name
        self._authentication_required = authentication_required
        self._inputs = {x.key: x for x in inputs}
        self._outputs = {x.key: x for x in outputs}
        self.messenger = None
        self.localization = Localization(self.localization_filename)

    def _set_app_io_value(self, key: str, value: Any | None, app_ios: Dict[str, AppIO]):
        app_io = app_ios[key]
        app_io.value = value
        if not app_io.validate():
            raise ValueError(f"Invalid value for AppIO {key}: {value}")

    def set_input(self, key: str, value: Any | None):
        self._set_app_io_value(key, value, self._inputs)

    def get_input(self, key: str) -> Any | None:
        return self._inputs[key].value
        
    def set_output(self, key: str, value: Any | None):
        self._set_app_io_value(key, value, self._outputs)

    def get_output(self, key: str) -> Any | None:
        return self._outputs[key].value
    
    def set_messenger(self, messenger: AppMessenger):
        self.messenger = messenger

    @abstractmethod
    def run(self):
        raise NotImplementedError("@abstractmethod")

    def render_input(self) -> Tuple[bool, bool]:
        valid_input = True
        value_changed = False
        for app_io in self._inputs.values():
            _valid_input, _value_changed = app_io.render_input()
            valid_input = valid_input and _valid_input
            value_changed = value_changed or _value_changed
        return valid_input, value_changed

    def render_output(self):
        for app_io in self._outputs.values():
            app_io.render_output()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "key": self.key,
            "inputs": {k: v.to_dict() for k, v in self._inputs.items()},
            "outputs": {k: v.to_dict() for k, v in self._outputs.items()}
        }
    
    @staticmethod
    @abstractmethod
    def input_validators() -> Dict[str, Callable[[Any], bool]]:
        raise NotImplementedError("@abstractmethod")
    
    @staticmethod
    @abstractmethod
    def output_validators() -> Dict[str, Callable[[Any], bool]]:
        raise NotImplementedError("@abstractmethod")
    

ValidatorSet = Dict[str, Callable[[Any], bool]]