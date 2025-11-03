import time
import pandas as pd
from io import StringIO
from datetime import date
from webapp.app import App
from typing import Dict, Callable, Any

from lib.oecd_inflation.oecd_inflation import OecdInflation, Frequency


class OecdInflationApp(App):
    
    def run(self):
        assert self.messenger is not None
        self.messenger.set_message_key("generating_table")
        date_ = self.get_input("date")
        assert isinstance(date_, date)
        year, month = date_.year, date_.month

        frequency_index = self.get_input("frequency")
        assert isinstance(frequency_index, int)
        frequency = Frequency(("M", "Q", "A")[frequency_index])

        table = OecdInflation().generate_dataframe(year, month, frequency)

        status = self.localization.get_translation("no_data" if table is None else "success")
        table = pd.DataFrame() if table is None else table

        csv_buffer = StringIO()
        table.to_csv(csv_buffer, sep=";", index_label='Monat')

        self.set_output("status", status)
        self.set_output("table", table)
        self.set_output("file", csv_buffer.getvalue())
        time.sleep(2)

    @staticmethod
    def input_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}
    
    @staticmethod
    def output_validators() -> Dict[str, Callable[[Any], bool]]:
        return {}
    
