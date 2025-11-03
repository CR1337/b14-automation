from __future__ import annotations
import os
import json
from typing import Dict, List
import streamlit as st
from dataclasses import dataclass


LANGUAGES_FILENAME: str = os.path.join("localization", "languages.json")


@st.cache_data
def _translations(localization_filename: str) -> Dict[str, Dict[str, str]]:
    try:
        with open(localization_filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except OSError:
        return {}

@st.cache_data
def _languages() -> Dict[str, Dict[str, str]]:
    with open(LANGUAGES_FILENAME, 'r', encoding='utf-8') as file:
        return json.load(file)
    

@dataclass
class Language:

    key: str
    name: str
    flag: str

    @classmethod
    def from_file(cls) -> List[Language]:
        languages = []
        for key, data in _languages().items():
            name = data["name"]
            flag = data["flag"]
            languages.append(cls(key, name, flag))
        return languages
    
    def __hash__(self) -> int:
        return hash(f"{self.key}{self.name}{self.flag}")
    

LANGUAGES: Dict[str, Language] = {
    language.key: language for language in Language.from_file()
}


class Localization:

    _localization_filename: str

    @staticmethod
    def get_current_language() -> Language:
        return st.session_state['language']

    @staticmethod
    def set_current_language(language: Language):
        st.session_state['language'] = language
    
    def __init__(self, localization_filename: str):
        self._localization_filename = localization_filename

    def get_translation(self, key: str, language: Language | None = None) -> str:
        return _translations(self._localization_filename)[key][language.key if language else self.get_current_language().key]
