import time
import pandas as pd
from io import StringIO
from datetime import date
from webapp.app import App
from typing import Dict, Callable, Any

from lib.oecd_inflation.oecd_inflation import OecdInflation


class OecdInflationApp(App):

    def initialize(self, language: str):
        assert self.messenger is not None
        self.language = language
        self.messenger.set_message({
            "de": "Initialisiere...",
            "en": "Initializing..."
        })
        time.sleep(1)
    
    def run(self):
        assert self.messenger is not None
        self.messenger.set_message({
            "de":"Generiere Tabelle...", 
            "en": "Generating Table..."
        })
        date_ = self.get_input("date")
        assert isinstance(date_, date)
        year, month = date_.year, date_.month

        table = OecdInflation().generate_dataframe(year, month)

        if table is None:
            if self._language == "de":
                status = "Für den ausgewählten Monat liegen keine Daten vor."
            else:
                status = "There is no data available for the selected month."
            table = pd.DataFrame()
        else:
            if self._language == "de":
                status = "Die Tabelle wurde erfolgreich erstellt."
            else:
                status = "The table was generated successfully."



        csv_buffer = StringIO()
        table.to_csv(csv_buffer, sep=";", index_label='Monat')

        self.set_output("status", status)
        self.set_output("table", table)
        self.set_output("file", csv_buffer.getvalue())
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
    
