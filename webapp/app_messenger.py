from typing import Dict
from threading import Lock, Event

class AppMessenger:
    
    _lock: Lock
    message: Dict[str, str]
    _is_done: Event

    def __init__(self):
        self._lock = Lock()
        self.message = {}
        self._is_done = Event()

    def set_is_done(self):
        self._is_done.set()

    @property
    def is_done(self) -> bool:
        return self._is_done.is_set()

    def get_message(self, language: str) -> str:
        # TODO: make this nicer
        if language not in self.message:
            if "de" in self.message:
                return self.message["de"]
            elif "en" in self.message:
                return self.message["en"]
            elif len(self.message) > 0:
                return self.message[list(self.message.keys())[0]]
            else:
                return ""
        else:
            return self.message[language]
        
    def set_message(self, message: Dict[str, str]):
        self.message = message

    def clear_message(self):
        self.message = {}
    

MESSENGERS: Dict[str, AppMessenger] = {}
