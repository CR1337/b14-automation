import time
from datetime import date
from webapp.app import App
from typing import Dict, Callable, Any

from lib.auto_text.erwerbslosigkeit import ErwerbslosigkeitTextGenerator


class TextGenerationApp(App):

    _text_generator: ErwerbslosigkeitTextGenerator

    def initialize(self, language: str):
        assert self.messenger is not None
        self.language = language
        self.messenger.set_message({
            "de": "Initialisiere Textgenerator...",
            "en": "Initializing text generator..."
        })
        topic_index = self.get_input("topic")
        match topic_index:
            case 0:  # unemploment rate
                self._text_generator = ErwerbslosigkeitTextGenerator.construct()
            case _:
                raise ValueError(f"Invalid topic index: {topic_index}")
        time.sleep(2)
    
    def run(self):
        assert self.messenger is not None
        self.messenger.set_message({
            "de":"Lade Daten von Eurostat...", 
            "en": "Loading data from Eurostat..."
        })
        date_ = self.get_input("date")
        assert isinstance(date_, date)
        year, month = date_.year, date_.month
        self._text_generator.request_data(year, month)
        time.sleep(1)

        self.messenger.set_message({
            "de":"Erstelle Text...", 
            "en": "Creating text..."
        })
        text = self._text_generator.generate()

        if text is None:
            if self._language == "de":
                status = "Für den ausgewählten Monat liegen keine Daten vor."
            else:
                status = "There is no data available for the selected month."
            text = ""
        else:
            if self._language == "de":
                status = "Der Text wurde erfolgreich erstellt."
            else:
                status = "The text was generated successfully."

        self.set_output("status", status)
        self.set_output("text", text)
        self.set_output("file", text)
        time.sleep(2)
        
    
    def destroy(self):
        assert self.messenger is not None
        self.messenger.clear_message()

    @staticmethod
    def input_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}
    
    @staticmethod
    def output_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}