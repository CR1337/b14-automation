import sdmx
import pandas as pd
from typing import Any, Dict, List


class SdmxDataKey:

    ALL: str = "__ALL__"
    
    _values: List[List[str]]

    def __init__(self):
        self._values = []

    def _adjust_size(self, index):
        while index >= len(self._values):
            self._values.append([])

    def add_value(self, value: str, index: int = 0):
        self.add_values([value], index)

    def add_values(self, values: List[str], index: int = 0):
        index = index or len(self._values)
        self._adjust_size(index)
        self._values[index].extend("*" if v == self.ALL else v for v in values)

    def __str__(self) -> str:
        values = (set(vs) for vs in self._values)
        return ".".join("+".join(v for v in vs) for vs in values)


class SdmxDataLoader:

    _client: sdmx.Client
    
    def __init__(self, source_id: str):
        self._client = sdmx.Client(source_id)

    def load(self, resource_id: str, key: SdmxDataKey, parameters: Dict[str, Any]) -> pd.DataFrame:
        data_message = self._client.data(resource_id, key=str(key), params=parameters)
        df = sdmx.to_pandas(data_message).to_frame()
        return df
