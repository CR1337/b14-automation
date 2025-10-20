from dataclasses import dataclass
from typing import Any, Dict, Tuple, Callable, Type, ClassVar
from datetime import datetime, date, time
import pandas as pd
import inspect
from webapp.app_io.app_io_type import AppIOType
from webapp.app_io.app_io_value import AppIoValue
from webapp.renderers import Renderer, BoolInputRenderer, IntegerInputRenderer, FloatInputRenderer, StringInputRenderer, DatetimeInputRenderer, DateInputRenderer, TimeInputRenderer, SelectionInputRenderer, FileInputRenderer, TableInputRenderer, BoolOutputRenderer, StringOutputRenderer, DatetimeOutputRenderer, DateOutputRenderer, TimeOutputRenderer, FileOutputRenderer, BinaryFileOutputRenderer, TableOutputRenderer


@dataclass
class AppIO:
    key: str
    name: Dict[str, str]
    type_: AppIOType

    is_input: bool

    can_be_none: bool
    default: Any | None
    validator: Callable[[Any], bool]

    parameters: Dict[str, Any]

    renderer: Renderer
    value: AppIoValue

    TYPES: ClassVar[Dict[AppIOType, Type]] = {
        AppIOType.BOOL: bool,
        AppIOType.INTEGER: int,
        AppIOType.FLOAT: float,
        AppIOType.STRING: str,
        AppIOType.FILENAME: str,
        AppIOType.URL: str,
        AppIOType.DATETIME: datetime,
        AppIOType.DATE: date,
        AppIOType.TIME: time,
        AppIOType.SELECTION: int,
        AppIOType.FILE: str,
        AppIOType.BINARY_FILE: bytes,
        AppIOType.TABLE: pd.DataFrame
    }

    TYPE_NAMES: ClassVar[Dict[str, AppIOType]] = {
        "bool": AppIOType.BOOL,
        "int": AppIOType.INTEGER,
        "float": AppIOType.FLOAT,
        "str": AppIOType.STRING,
        "filename": AppIOType.FILENAME,
        "url": AppIOType.URL,
        "datetime": AppIOType.DATETIME,
        "date": AppIOType.DATE,
        "time": AppIOType.TIME,
        "selection": AppIOType.SELECTION,
        "file": AppIOType.FILE,
        "binary_file": AppIOType.BINARY_FILE,
        "table": AppIOType.TABLE,
    }

    INPUT_RENDERERS: ClassVar[Dict[AppIOType, Type[Renderer]]] = {
        AppIOType.BOOL: BoolInputRenderer,
        AppIOType.INTEGER: IntegerInputRenderer,
        AppIOType.FLOAT: FloatInputRenderer,
        AppIOType.STRING: StringInputRenderer,
        AppIOType.FILENAME: StringInputRenderer,
        AppIOType.URL: StringInputRenderer,
        AppIOType.DATETIME: DatetimeInputRenderer,
        AppIOType.DATE: DateInputRenderer,
        AppIOType.TIME: TimeInputRenderer,
        AppIOType.SELECTION: SelectionInputRenderer,
        AppIOType.FILE: FileInputRenderer,
        AppIOType.BINARY_FILE: FileInputRenderer,
        AppIOType.TABLE: TableInputRenderer
    }

    OUTPUT_RENDERERS: ClassVar[Dict[AppIOType, Type[Renderer]]] = {
        AppIOType.BOOL: BoolOutputRenderer,
        AppIOType.INTEGER: StringOutputRenderer,
        AppIOType.FLOAT: StringOutputRenderer,
        AppIOType.STRING: StringOutputRenderer,
        AppIOType.FILENAME: StringOutputRenderer,
        AppIOType.URL: StringOutputRenderer,
        AppIOType.DATETIME: DatetimeOutputRenderer,
        AppIOType.DATE: DateOutputRenderer,
        AppIOType.TIME: TimeOutputRenderer,
        AppIOType.SELECTION: StringOutputRenderer,
        AppIOType.FILE: FileOutputRenderer,
        AppIOType.BINARY_FILE: BinaryFileOutputRenderer,
        AppIOType.TABLE: TableOutputRenderer
    }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "type": str(self.type_),
            "is_input": self.is_input,
            "can_be_none": self.can_be_none,
            "default": str(self.default),
            "validator": inspect.getsource(self.validator),
            "parameters": self.parameters,
            "value_type": str(self.type_),
            "value": str(self.value.get())
        }

    @classmethod
    def make_input(
        cls,
        key: str,
        name: Dict[str, str],
        type_: AppIOType,
        can_be_none: bool = False,
        default: Any | None = None,
        validator: Callable[[Any], bool] | None = None,
        parameters: Dict[str, Any] | None = None
    ):
        return cls._make(key, name, type_, True, can_be_none, default, validator, parameters or {})

    @classmethod
    def make_output(
        cls,
        key: str,
        name: Dict[str, str],
        type_: AppIOType,
        can_be_none: bool = False,
        default: Any | None = None,
        validator: Callable[[Any], bool] | None = None,
        parameters: Dict[str, Any] | None = None
    ):
        return cls._make(key, name, type_, False, can_be_none, default, validator, parameters or {})

    @classmethod
    def _make(
        cls,
        key: str,
        name: Dict[str, str],
        type_: AppIOType,
        is_input: bool,
        can_be_none: bool,
        default: Any | None,
        validator: Callable[[Any], bool] | None,
        parameters: Dict[str, Any]
    ):
        if default is not None and validator is not None:
            if not validator(default):
                raise ValueError(
                    f"Invalid default value for AppIO {key}: {default}"
                )

        renderer = (cls.INPUT_RENDERERS[type_] if is_input else cls.OUTPUT_RENDERERS[type_])()

        if type_ == AppIOType.SELECTION:
            default = default or 0

        value = AppIoValue(key, type_, parameters)
        value.set(default)

        return cls(
            key=key,
            name=name,
            type_=type_,
            is_input=is_input,
            can_be_none=can_be_none,
            default=default,
            validator=validator or (lambda _: True),
            parameters=parameters,
            renderer=renderer,
            value=value
        )

    @property
    def is_output(self) -> bool:
        return not self.is_input
    
    def __repr__(self) -> str:
        return f"{self.key=}, {self.name=}, {self.type_=}, {self.is_input=}"

    def validate(self) -> bool:
        if self.can_be_none and self.value.get() is None:
            return True
        if not isinstance(self.value.get(), self.TYPES[self.type_]):
            return False
        return self.validator(self.value.get())
    
    def render_input(self) -> Tuple[bool, bool]:
        old_value = self.value.get()
        new_value = self.renderer.render(self)
        is_valid = self.validate()
        self.value.set(new_value)
        return is_valid, old_value != new_value

    def render_output(self):
        self.renderer.render(self)