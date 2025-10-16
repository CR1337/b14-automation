from abc import ABC, abstractmethod
from typing import Any
from webapp.localization import Localization, Language


class Renderer(ABC):
    
    @property
    def language(self) -> Language:
        return Localization.get_current_language()
    
    @abstractmethod
    def render(self, app_io: Any):
        raise NotImplementedError("@abstractmethod")
