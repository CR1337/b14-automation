import pandas as pd
from io import StringIO
from datetime import datetime

from lib.network.get import get_from_url


class OecdInflation:
    URL = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/.M.N.CPI.PA._T.N.GY?format=csvfile&startPeriod={year}-{month:02d}"
    DECIMAL_DIGITS = 2

    TRANSLATIONS = {
        "countries": {
            "MEX": "Mexiko",
            "BRA": "Brasilien",
            "ARG": "Argentinien",
            "ZAF": "Südafrika",
            "CAN": "Kanada",
            "USA": "Vereinigte Staaten",
            "IDN": "Indonesien",
            "JPN": "Japan",
            "DEU": "Deutschland",
            "TUR": "Türkei",
            "CHN": "China",
            "GBR": "Vereinigtes Königreich",
            "ITA": "Italien",
            "FRA": "Frankreich",
            "RUS": "Russische Föderation",
            "SAU": "Saudi Arabien",
            "KOR": "Korea, Republik",
            "IND": "Indien"
        },
        "months": [
            "Jan",
            "Feb",
            "Mrz",
            "Apr",
            "Mai",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Okt",
            "Nov",
            "Dez"
        ]
    }
    COUNTRY_TRANSLATIONS = TRANSLATIONS['countries']
    MONTHS_TRANSLATIONS = TRANSLATIONS['months']

    def generate_dataframe(self, year: int, month: int) -> pd.DataFrame | None:
        response = get_from_url(url=self.URL.format(year=year, month=month), timeout=15)
        csv_data = response.text

        df = pd.read_csv(StringIO(csv_data), sep=",")

        if "NoRecordsFound" in df.columns:
            return None

        df['country'] = df['REF_AREA'].apply(
            lambda x: f"{self.COUNTRY_TRANSLATIONS[x]}"
            if x in self.COUNTRY_TRANSLATIONS else None
        )
        df = df.dropna(subset=['country'])

        df['time'] = df['TIME_PERIOD'].apply(
            lambda x: f"{x[:4]}/{x[5:]}/01"
        )
        df = df.sort_values(by='TIME_PERIOD')

        df['value'] = df['OBS_VALUE'].apply(
            lambda x: '{0:.1f}'.format(round(x, self.DECIMAL_DIGITS)).replace('.', ',')
        )

        table = df.pivot(index='time', columns='country', values='value')
        table = table.reindex(
            sorted(table.columns), 
            axis=1
        )
        table = table.loc[sorted(
            table.index,
            key=lambda date_str: datetime.strptime(date_str, "%Y/%m/%d")
        )]

        return table
