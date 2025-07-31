import os
import json
from typing import Dict, List
import streamlit as st


LANGUAGES_FILENAME: str = os.path.join("localization", "languages.json")


@st.cache_data
def _translations(filename: str) -> Dict[str, Dict[str, str]]:
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

@st.cache_data
def _languages() -> Dict[str, Dict[str, str]]:
    with open(LANGUAGES_FILENAME, 'r', encoding='utf-8') as file:
        return json.load(file)


class Localization:
    _localization_filename: str

    def __init__(self, localization_filename: str):
        self._localization_filename = localization_filename

    @classmethod
    def get_all_languages(cls) -> List[str]:
        return list(_languages().keys())
    
    def get_language_name(self, language: str) -> str:
        return _languages()[language]["name"]
    
    def get_language_flag(self, language: str) -> str:
        return _languages()[language]["flag"]
    
    def get(self, key: str, language: str):
        return self.get_translations(key)[language]
    
    def get_translations(self, key: str) -> Dict[str, str]:
        return _translations(self._localization_filename)[key]
    
    def __hash__(self) -> int:
        return hash(self._localization_filename)
