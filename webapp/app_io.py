from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Tuple, Callable, Type, ClassVar
from datetime import datetime, timedelta, date, time
import streamlit as st
import pandas as pd
import inspect


class AppIOType(Enum):
    BOOL = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    FILENAME = auto()
    URL = auto()
    DATETIME = auto()
    DATE = auto()
    TIME = auto()
    SELECTION = auto()
    FILE = auto()
    BINARY_FILE = auto()
    TABLE = auto()


@dataclass
class AppIO:
    key: str
    name: Dict[str, str]
    type: AppIOType

    is_input: bool

    can_be_none: bool
    default: Any | None
    validator: Callable[[Any], bool]

    parameters: Dict[str, Any]

    value: Any | None = None

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "type": str(self.type),
            "is_input": self.is_input,
            "can_be_none": self.can_be_none,
            "default": str(self.default),
            "validator": inspect.getsource(self.validator),
            "parameters": self.parameters,
            "value_type": str(type(self.value)),
            "value": str(self.value)
        }

    @classmethod
    def make_input(
        cls,
        key: str,
        name: Dict[str, str],
        type: AppIOType,
        can_be_none: bool = False,
        default: Any | None = None,
        validator: Callable[[Any], bool] | None = None,
        parameters: Dict[str, Any] | None = None
    ):
        return cls._make(key, name, type, True, can_be_none, default, validator, parameters or {})

    @classmethod
    def make_output(
        cls,
        key: str,
        name: Dict[str, str],
        type: AppIOType,
        can_be_none: bool = False,
        default: Any | None = None,
        validator: Callable[[Any], bool] | None = None,
        parameters: Dict[str, Any] | None = None
    ):
        return cls._make(key, name, type, False, can_be_none, default, validator, parameters or {})

    @classmethod
    def _make(
        cls,
        key: str,
        name: Dict[str, str],
        type: AppIOType,
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
        return cls(
            key=key,
            name=name,
            type=type,
            is_input=is_input,
            can_be_none=can_be_none,
            default=default,
            validator=validator or (lambda _: True),
            parameters=parameters
        )

    @property
    def is_output(self) -> bool:
        return not self.is_input
    
    def __repr__(self) -> str:
        return f"{self.key=}, {self.name=}, {self.type=}, {self.is_input=}"

    def validate(self) -> bool:
        if self.can_be_none and self.value is None:
            return True
        if not isinstance(self.value, self.TYPES[self.type]):
            return False
        return self.validator(self.value)
    
    def render_input(self, language: str) -> Tuple[bool, bool]:
        old_value = self.value
        match self.type:
            case AppIOType.BOOL:
                self.value = st.checkbox(
                    label=self.name[language], 
                    value=bool(self.value), 
                    key=self.key
                )

            case AppIOType.INTEGER:
                self.value = st.number_input(
                    label=self.name[language], 
                    value=self.value, 
                    min_value=self.parameters.get("min_value"),
                    max_value=self.parameters.get("max_value"),
                    step=self.parameters.get("step", 1),
                    format=self.parameters.get("format")
                )

            case AppIOType.FLOAT:
                self.value = st.number_input(
                    label=self.name[language], 
                    value=self.value, 
                    min_value=self.parameters.get("min_value"),
                    max_value=self.parameters.get("max_value"),
                    step=self.parameters.get("step", 0.001),
                    format=self.parameters.get("format")
                )

            case AppIOType.STRING | AppIOType.FILENAME | AppIOType.URL:
                placeholder = self.parameters.get("placeholder")
                if not placeholder:
                    filename = self.parameters.get("placeholder_from_file")
                    if filename:
                        with open(filename, 'r') as file:
                            placeholder = file.read()

                value = None
                value_filename = self.parameters.get("value_from_file")
                if value_filename:
                    with open(value_filename, 'r') as file:
                        value = file.read()


                if self.parameters.get("multiline", False):
                    self.value = st.text_area(
                        label=self.name[language], 
                        value=value or self.value, 
                        max_chars=self.parameters.get("max_chars"),
                        key=self.key,
                        placeholder=placeholder
                    )
                else:
                    self.value = st.text_input(
                        label=self.name[language], 
                        value=value or self.value, 
                        max_chars=self.parameters.get("max_chars"),
                        key=self.key,
                        type=self.parameters.get("type", "default"),
                        placeholder=placeholder
                    )

            case AppIOType.DATETIME:
                columns = st.columns(2)
                date_ = columns[0].date_input(
                    label=self.name[language],
                    value=self.value,
                    min_value=self.parameters.get("min_value"),
                    max_value=self.parameters.get("max_value"),
                    format=self.parameters.get("format", "YYYY-MM-DD"),
                    key=self.key
                ) or date.today()
                time_ = columns[0].time_input(
                    label="",
                    value=self.value,
                    key=self.key,
                    step=self.parameters.get("step", timedelta(minutes=15))
                ) or time(0, 0, 0, 0)
                date_time = datetime.combine(date_, time_)
                self.value = date_time

            case AppIOType.DATE:
                self.value = st.date_input(
                    label=self.name[language],
                    value=self.value,
                    min_value=self.parameters.get("min_value"),
                    max_value=self.parameters.get("max_value"),
                    format=self.parameters.get("format", "YYYY-MM-DD"),
                    key=self.key
                ) or date.today()  

            case AppIOType.TIME:
                self.value = st.time_input(
                    label="",
                    value=self.value,
                    key=self.key,
                    step=self.parameters.get("step", timedelta(minutes=15))
                ) or time(0, 0, 0, 0)           

            case AppIOType.SELECTION:
                options = self.parameters.get("options", {"de": [], "en": []})[language]
                try:
                    index = options.index(self.value)
                except ValueError:
                    index = 0
                selection = st.selectbox(
                    label=self.name[language],
                    options=options,
                    index=index,
                    key=self.key
                )
                self.value = options.index(selection)

            case AppIOType.FILE | AppIOType.BINARY_FILE:
                file = st.file_uploader(
                    label=self.name[language],
                    type=self.parameters.get("type"),
                    accept_multiple_files=False,
                    key=self.key
                )
                if file:
                    if self.type == AppIOType.FILE:
                        self.value = file.getvalue().decode(self.parameters.get("encoding", "utf-8"))
                    else:
                        self.value = file.getvalue()

            case AppIOType.TABLE:
                file = st.file_uploader(
                    label=self.name[language],
                    type=["csv"],
                    accept_multiple_files=False,
                    key=self.key
                )
                if file:
                    self.value = pd.read_csv(
                        file,
                        sep=self.parameters.get("sep"),
                        delimiter=self.parameters.get("delimiter")
                    )

            case _:
                raise RuntimeError("There is an unhandled AppIOType!")

        is_valid = self.validate()
        return is_valid, old_value != self.value

            

    def render_output(self, language: str):
        match self.type:
            case AppIOType.BOOL:
                st.text_input(
                    label=self.name[language],
                    value="Ja" if self.value else "Nein",
                    key=self.key,
                    disabled=True
                )

            case AppIOType.INTEGER | AppIOType.FLOAT | AppIOType.STRING | AppIOType.FILENAME | AppIOType.SELECTION | AppIOType.URL:
                if self.parameters.get("multiline", False):
                    st.text_area(
                        label=self.name[language],
                        value=str(self.value),
                        key=self.key,
                        disabled=True,
                        height="content"  # type: ignore
                    )
                else:
                    st.text_input(
                        label=self.name[language],
                        value=str(self.value),
                        key=self.key,
                        disabled=True
                    )

            case AppIOType.DATETIME:
                assert isinstance(self.value, datetime)
                st.text_input(
                    label=self.name[language],
                    value=datetime.strftime(self.value, "%Y-%m-%d %H:%M"),
                    key=self.key,
                    disabled=True
                )

            case AppIOType.DATE:
                assert isinstance(self.value, date)
                st.text_input(
                    label=self.name[language],
                    value=date.strftime(self.value, "%Y-%m:%d"),
                    key=self.key,
                    disabled=True
                )

            case AppIOType.TIME:
                assert isinstance(self.value, time)
                st.text_input(
                    label=self.name[language],
                    value=time.strftime(self.value, "%H:%M"),
                    key=self.key,
                    disabled=True
                )

            case AppIOType.FILE:
                filename = self.parameters.get("filename", "data.txt")
                if self.parameters.get("prefix_language", False):
                    filename = f"{language}_{filename}"
                if self.parameters.get("prefix_datetime", False):
                    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                st.download_button(
                    label=self.name[language],
                    data=str(self.value),
                    file_name=filename,
                    mime=self.parameters.get("mime", "text/plain"),
                    key=self.key,
                    use_container_width=True
                )
                
            case AppIOType.BINARY_FILE:
                assert isinstance(self.value, bytes)
                filename = self.parameters.get("filename", "data.bin")
                if self.parameters.get("prefix_language", False):
                    filename = f"{language}_{filename}"
                if self.parameters.get("prefix_datetime", False):
                    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                st.download_button(
                    label=self.name[language],
                    data=self.value,
                    file_name=filename,
                    mime=self.parameters.get("mime", "application/octet-stream"),
                    key=self.key,
                    use_container_width=True
                )

            case AppIOType.TABLE:
                st.dataframe(
                    data=self.value,
                    key=self.key
                )

            case _:
                raise RuntimeError("There is an unhandled AppIOType!")