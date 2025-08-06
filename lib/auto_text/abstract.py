from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict
from datetime import datetime

# from lib.eurostat.eurostat_api.dataset import EurostatDataset

from ..eurostat.eurostat_api.dataset import EurostatDataset


class EurostatAutoTextGenerator(ABC):

    _name: str
    _datasets: Dict[str, EurostatDataset]
    TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

    @classmethod
    def construct(cls, name: str) -> EurostatAutoTextGenerator:
        return cls(name)

    def __init__(self, name: str):
        self._name = name
        self._datasets = {}

    def add_dataset(self, key: str, dataset: EurostatDataset):
        assert(key not in self._datasets)
        self._datasets[key] = dataset

    @abstractmethod
    def request_data(self, year: int, month: int):
        raise NotImplementedError("@abstractmethod")
    
    @abstractmethod
    def generate(self) -> str | None:
        raise NotImplementedError("@abstractmethod")

    def generate_filename(self) -> str:
        return f"{self.TIMESTAMP}_{self._name}.txt"
