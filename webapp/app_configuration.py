from dataclasses import dataclass
from typing import Dict, List, Tuple
from webapp.app_io.app_io import AppIO


@dataclass
class AppConfiguration:
    name: Dict[str, str]
    authentication_required: bool
    inputs: List[AppIO]
    outputs: List[AppIO]
    input_key_mappings: Dict[str, str]
    output_key_mappings: Dict[str, str]

    def to_tuple(self) -> Tuple[
        Dict[str, str], 
        bool, 
        List[AppIO], 
        List[AppIO], 
        Dict[str, str], 
        Dict[str, str]
    ]:
        return (
            self.name,
            self.authentication_required,
            self.inputs,
            self.outputs,
            self.input_key_mappings,
            self.output_key_mappings
        )
    