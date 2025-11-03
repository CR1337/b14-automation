from webapp.app import App, ValidatorSet
import pandas as pd
from io import StringIO

from lib.wdi.wdi import Wdi
from lib.sdmx.data_loader import SdmxDataKey, SdmxDataLoader


class WorldPopulationApp(App):
   
    def run(self):
        assert self.messenger is not None
        success = True

        self.messenger.set_message_key("loading_weo_data")
        weo_key = SdmxDataKey()
        weo_key.add_value(SdmxDataKey.ALL)
        weo_key.add_value("PPPSH")
        weo_key.add_value("A")
        weo_loader = SdmxDataLoader("IMF_DATA")
        weo_parameters = {"startPeriod": 2020}
        try:
            weo_df = weo_loader.load("WEO", weo_key, weo_parameters)
            weo_df = weo_df.reset_index()
        except Exception:
            weo_df = pd.DataFrame()
            success = False

        self.messenger.set_message_key("loading_wdi_data")
        try:
            wdi_df = Wdi.get(
                indicators=[
                    "SP.POP.TOTL",
                    "SP.POP.GROW",
                    "SP.POP.65UP.TO",
                    "SP.POP.65UP.TO.ZS",
                    "SP.DYN.LE00.IN",
                    "SP.DYN.TFRT.IN"
                ],
                start_year=2020
            )
            wdi_df = wdi_df.reset_index()
        except Exception:
            wdi_df = pd.DataFrame()
            success = False

        self.messenger.set_message_key("preparing_result")
        self.set_output("weo_data", weo_df)
        self.set_output("wdi_data", wdi_df)

        weo_csv_buffer = StringIO()
        weo_df.to_csv(weo_csv_buffer, sep=";", index=False)
        self.set_output("weo_file", weo_csv_buffer.getvalue())

        wdi_csv_buffer = StringIO()
        wdi_df.to_csv(wdi_csv_buffer, sep=";", index=False)
        self.set_output("wdi_file", wdi_csv_buffer.getvalue())

        status = self.localization.get_translation("success" if success else "error")
        self.set_output("status", status)

    @staticmethod
    def input_validators() -> ValidatorSet:
        return {}
    
    @staticmethod
    def output_validators() -> ValidatorSet:
        return {}
    