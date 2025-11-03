import streamlit as st
from typing import Any, Dict
from webapp.app_io.app_io_type import AppIOType


class AppIoValue:

    _key: str
    _is_rendered: bool
    _type: AppIOType
    _parameters: Dict[str, Any] | None

    def __init__(self, key: str, type_: AppIOType, parameters: Dict[str, Any] | None):
        self._key = f"{key}_AppIoValue"
        self._type = type_
        self._parameters = parameters
        self._is_rendered = False

    def set(self, value: Any):
        st.session_state[self._key] = value

    def get(self) -> Any:
        if self._key not in st.session_state:
            st.session_state[self._key] = None
        return st.session_state[self._key]

    def set_is_rendered(self):
        self._is_rendered = True

    @property
    def key(self) -> str:
        return self._key
    