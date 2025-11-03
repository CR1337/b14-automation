from typing import Dict
from threading import Event
from webapp.localization import Localization


class AppMessenger:
    
    _localization: Localization
    _message_key: str | None
    _is_done: Event

    def __init__(self, localization: Localization):
        self._localization = localization
        self._message_key = None
        self._is_done = Event()

    def set_is_done(self):
        self._is_done.set()

    @property
    def is_done(self) -> bool:
        return self._is_done.is_set()

    @property
    def message(self) -> str:
        if self._message_key is None:
            return ""
        return self._localization.get_translation(self._message_key) or ""

    def set_message_key(self, key: str):
        self._message_key = key

    def clear_message_key(self):
        self._message_key = None


MESSENGERS: Dict[str, AppMessenger] = {}
