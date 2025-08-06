import pandas as pd

import requests
import urllib3
import ssl

import platform
from io import StringIO
from datetime import datetime


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

match platform.system():
    case "Windows":
        def get_from_url(url: str) -> requests.Response:  # type: ignore
            '''
            Windows version
            '''
            return requests.get(url=url, timeout=10, verify=False)
    case _:
        def get_from_url(**kwargs) -> requests.Response:
            '''
            Linux version
            https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled/71646353#71646353
            '''
            class CustomHttpAdapter (requests.adapters.HTTPAdapter):  # type: ignore
                # "Transport adapter" that allows us to use custom ssl_context.

                def __init__(self, ssl_context=None, **kwargs):
                    self.ssl_context = ssl_context
                    super().__init__(**kwargs)

                def init_poolmanager(self, connections, maxsize, block=False):
                    self.poolmanager = urllib3.poolmanager.PoolManager(
                        num_pools=connections, maxsize=maxsize,
                        block=block, ssl_context=self.ssl_context)

            def get_legacy_session() -> requests.Session:
                ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
                session = requests.session()
                session.mount('https://', CustomHttpAdapter(ctx))
                return session

            return get_legacy_session().get(**kwargs)


def generate_dataframe(year: int, month: int) -> pd.DataFrame | None:
    response = get_from_url(url=URL.format(year=year, month=month), timeout=15)
    csv_data = response.text

    df = pd.read_csv(StringIO(csv_data), sep=",")

    if "NoRecordsFound" in df.columns:
        return None

    df['country'] = df['REF_AREA'].apply(
        lambda x: f"{COUNTRY_TRANSLATIONS[x]}"
        if x in COUNTRY_TRANSLATIONS else None
    )
    df = df.dropna(subset=['country'])

    df['time'] = df['TIME_PERIOD'].apply(
        lambda x: f"{x[:4]}/{x[5:]}/01"
    )
    df = df.sort_values(by='TIME_PERIOD')

    df['value'] = df['OBS_VALUE'].apply(
        lambda x: '{0:.1f}'.format(round(x, DECIMAL_DIGITS)).replace('.', ',')
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
