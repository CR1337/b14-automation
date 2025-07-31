from __future__ import annotations
from lib.auto_text.abstract import EurostatAutoTextGenerator

from lib.eurostat.eurostat_api.dataset import EurostatDataset
from lib.eurostat.eurostat_api.filters import DimensionFilter, TimePeriodFilter

import lib.auto_text.util as u
import pandas as pd
from typing import List, Tuple


class ErwerbslosigkeitTextGenerator(EurostatAutoTextGenerator):
    GEO: List[str] = [
        "EU27_2020",
        "EA20",
        "BE",
        "BG",
        "CZ",
        "DK",
        "DE",
        "EE",
        "IE",
        "EL",
        "ES",
        "FR",
        "HR",
        "IT",
        "CY",
        "LV",
        "LT",
        "LU",
        "HU",
        "MT",
        "NL",
        "AT",
        "PL",
        "PT",
        "RO",
        "SI",
        "SK",
        "SE",
        "FI",
    ]

    TEMPLATE: str = """
EU-weite Erwerbslosigkeit liegt im {month_year} bei {unemployment_tot_perc_eu}{nbsp}%

Deutschland mit {unemployment_tot_perc}{nbsp}% auf Rang {rank_de}

In Deutschland waren im {month_year} rund {unemployment_tot_perc}{nbsp}% der 15- bis 74-jährigen Erwerbspersonen ohne Arbeit. Im EU-Vergleich war {unemployment_tot_perc_countries}.

EU-weit waren im {month_year} rund {unemployment_tot_tot_eu}{nbsp}Millionen Menschen ohne Arbeit. Das entsprach einer Erwerbslosenquote von {unemployment_tot_perc_eu}{nbsp}%. Die Erwerbs­losen­quote in der Euro­zone lag mit {unemployment_tot_perc_ez}{nbsp}% {eu_ez_comp} dem Niveau der gesamten EU. Der größte Mangel an Arbeitsplätzen herrschte in {unemployment_tot_perc_countries_highest}.

Die Jugenderwerbslosenquote in der EU-27 betrug im {month_year} rund {unemployment_lt25_perc_eu}{nbsp}% und betrug damit {unemployment_lt25_perc_eu_rel}{nbsp}% des Durchschnitts aller Erwerbstätigen. Die niedrigsten Quoten verzeichneten {unemployment_lt25_perc_countries_lowest}. Am höchsten waren die Anteile in {unemployment_lt25_perc_countries_highest}.{countries_no_lt25}

Methodik

Die Erwerbslosenquote nach der Definition der ILO ist der Anteil der Erwerbslosen an den Erwerbspersonen.

Die Erwerbspersonen setzen sich aus den Erwerbstätigen und den Erwerbslosen zusammen.

Erwerbstätige im Sinne der Internationalen Arbeitsorganisation (ILO)-Definition sind Personen im Alter von 15 Jahren und mehr, die mindestens eine Stunde in der Woche gegen Entgelt irgendeiner beruflichen Tätigkeit nachgehen beziehungsweise in einem Arbeitsverhältnis stehen.

Quelle

Die monatlichen Daten zur Erwerbslosigkeit finden Sie in der Eurostat Datenbank, weitere Informationen in Statistics Explained. Detaillierte Daten zur Erwerbslosigkeit in Deutschland gibt es auf den nationalen Themenseiten.
""".strip()

    _year: int
    _month: int

    def _data_available(self) -> bool:
        df = self._df("TOTAL", "PC_ACT")
        df = df[df["geo"].isin(["DE", "EU27_2020"])]
        return len(df) == 2

    def _last_5_months(self, year: int, month: int):
        months = []
        for i in range(5):
            y = year
            m = month - i
            while m <= 0:
                m += 12
                y -= 1
            months.append(f"{y:04d}-{m:02d}")
        return months

    def _time(self) -> str:
        return f"{self._year:04d}-{self._month:02d}"

    def _df(self, age: str, unit: str) -> pd.DataFrame:
        df = self._datasets["data"].data.dataframe
        df = df[df["geo"].isin(self.GEO)].copy()
        df["observation"] = df["observation"].astype(float)
        df = df [
            (df["time"] == self._time())
            & (df["age"] == "TOTAL")
            & (df["unit"] == "PC_ACT")
        ]
        return df

    def _get_pairs(
        self, df: pd.DataFrame, n: int | None = None, case: str = "D"
    ) -> List[Tuple[str, str]]:
        pairs = list(
            zip(
                df["geo"].map(lambda g: u.COUNTRY_NAMES_CASED[g][case]), df["observation"]
            )
        )
        pairs = [p for p in pairs if not pd.isna(p[0])]
        if n is None:
            n = len(pairs)
        pairs = [(p[0], u.format_value(p[1])) for p in pairs][: min(n, len(pairs))]
        pairs = sorted(pairs, key=lambda p: p[1], reverse=False)
        return pairs

    def _pair_to_str(self, ps: List[Tuple[str, str]], i: int, unit: str = "%") -> str:
        return f"{ps[i][0]} ({ps[i][1]}{u.NBSP}{unit})"

    def month_year(self) -> str:
        return f"{u.MONTHS[self._month]} {self._year:04d}"

    def unemployment_tot_perc(self) -> str:
        df = self._df("TOTAL", "PC_ACT")
        df = df[df["geo"] == "DE"]
        value = df["observation"].values[0]
        return u.format_value(value)

    def rank_de(self) -> str:
        df = self._df("TOTAL", "PC_ACT")
        df = df[
            (df["geo"] != "EU27_2020")
            & (df["geo"] != "EA20")
        ]
        rank = (
            df["observation"].rank(method="min").astype(int)[df["geo"] == "DE"].iloc[0]
        )
        return str(rank)

    def unemployment_tot_perc_countries(self) -> str:
        df = self._df("TOTAL", "PC_ACT")
        df = df[
            (df["geo"] != "EU27_2020")
            & (df["geo"] != "EA20")
        ]
        df = df[df["observation"] < df.loc[df["geo"] == "DE", "observation"].iloc[0]]
        df = df.sort_values(by="observation")
        pairs = self._get_pairs(df)

        if len(pairs) == 0:
            return "dies die niedrigste Erwerbslosenquote"

        template = "die Erwerbslosenquote {eg_or_only} in {country_list} noch niedriger"

        if len(pairs) < 4:
            return template.format(
                eg_or_only="nur",
                country_list=u.enumerate_terms(
                    [self._pair_to_str(pairs, i) for i in range(len(pairs))]
                ),
            )
        else:
            indices = (0, len(pairs) // 2, len(pairs) - 1)
            return template.format(
                eg_or_only="beispielsweise",
                country_list=u.enumerate_terms(
                    [self._pair_to_str(pairs, i) for i in indices]
                ),
            )

    def unemployment_tot_tot_eu(self) -> str:
        df = self._df("TOTAL", "THS_PER")
        df = df[df["geo"] == "EU27_2020"]
        value = df["observation"].values[0] / u.THOUSANDS_PER_MIILLION
        return u.format_value(value)

    def unemployment_tot_perc_eu(self) -> str:
        df = self._df("TOTAL", "PC_ACT")
        df = df[df["geo"] == "EU27_2020"]
        value = df["observation"].values[0]
        return u.format_value(value)

    def unemployment_tot_perc_ez(self) -> str:
        df = self._df("TOTAL", "PC_ACT")
        df = df[df["geo"] == "EA20"]
        value = df["observation"].values[0]
        return u.format_value(value)

    def eu_ez_comp(self) -> str:
        eu_value = u.from_str(self.unemployment_tot_perc_eu())
        ez_value = u.from_str(self.unemployment_tot_perc_ez())
        if eu_value > ez_value:
            return "unter"
        elif eu_value < ez_value:
            return "über"
        else:
            return "auf"

    def unemployment_tot_perc_countries_highest(self) -> str:
        n_countries = 2
        df = self._df("TOTAL", "PC_ACT")
        df = df[
            (df["geo"] != "EU27_2020")
            & (df["geo"] != "EA20")
        ]
        df = df.sort_values(by="observation", ascending=False)
        pairs = self._get_pairs(df, n_countries)

        return u.enumerate_terms([self._pair_to_str(pairs, i) for i in range(n_countries)])

    def unemployment_lt25_perc_eu(self) -> str:
        df = self._df("Y_LT25", "PC_ACT")
        df = df[df["geo"] == "EU27_2020"]
        value = df["observation"].values[0]
        return u.format_value(value)

    def unemployment_lt25_perc_eu_rel(self) -> str:
        value_lt25 = u.from_str(self.unemployment_lt25_perc_eu())
        value_tot = u.from_str(self.unemployment_tot_perc_eu())
        result = (value_lt25 / value_tot) * 100
        return u.format_value(result)

    def unemployment_lt25_perc_countries_lowest(self) -> str:
        df = self._df("Y_LT25", "PC_ACT")
        df = df[
            (df["geo"] != "EU27_2020")
            & (df["geo"] != "EA20")
        ]
        df = df.sort_values(by="observation")
        n_countries = min(3, len(df))
        pairs = self._get_pairs(df, n_countries, case="N")

        return u.enumerate_terms([self._pair_to_str(pairs, i) for i in range(n_countries)])

    def unemployment_lt25_perc_countries_highest(self) -> str:
        df = self._df("Y_LT25", "PC_ACT")
        df = df[
            (df["geo"] != "EU27_2020")
            & (df["geo"] != "EA20")
        ]
        df = df.sort_values(by="observation", ascending=False)
        n_countries = min(2, len(df))
        pairs = self._get_pairs(df, n_countries)

        return u.enumerate_terms([self._pair_to_str(pairs, i) for i in range(n_countries)])

    def countries_no_lt25(self) -> str:
        df = self._df("Y_LT25", "PC_ACT")
        df = df[
            (df["geo"] != "EU27_2020")
            & (df["geo"] != "EA20")
        ]

        all_country_ids = set(self.GEO) - set(["EU27_2020", "EA20"])
        not_found_country_ids = [
            c for c in all_country_ids if c not in df["geo"].values
        ]
        nan_country_ids = (
            df.loc[(df["observation"].isna()) | df["observation"] == "-", "geo"]
            .astype(str)
            .tolist()
        )
        country_ids = nan_country_ids + not_found_country_ids
        countries = [u.COUNTRY_NAMES_CASED[cid]["N"] for cid in country_ids]

        sentence_suffix = (
            f"keine Jugenderwerbslosenquoten für {self.month_year()} geliefert.\n"
        )

        match len(countries):
            case 0:
                return ""
            case 1:
                return f"\n\n{countries[0]} hat {sentence_suffix}"
            case _:
                return f"\n\n{u.enumerate_terms(countries)} haben {sentence_suffix}"

    @classmethod
    def construct(cls) -> ErwerbslosigkeitTextGenerator:  # type: ignore
        generator = super().construct("erwerbslosigkeit")
        dataset = EurostatDataset("une_rt_m", "de")
        dimension_filter = DimensionFilter(dataset)
        dimension_filter.add("age", ["TOTAL", "Y_LT25"])
        dimension_filter.add("sex", ["T"])
        dimension_filter.add("s_adj", ["SA"])
        generator.add_dataset("data", dataset)
        return generator  # type: ignore
    
    def request_data(self, year: int, month: int):
        dataset = self._datasets["data"]
        time_period_filter = TimePeriodFilter(dataset)
        months = self._last_5_months(year, month)
        time_period_filter.add(TimePeriodFilter.Operators.GREATER_OR_EQUALS, months[-1])
        dataset.request_data()

        self._year = year
        self._month = month

    def generate(self) -> str | None:
        if not self._data_available():
            return None
        
        text = self.TEMPLATE.format(
            month_year=self.month_year(),
            unemployment_tot_perc=self.unemployment_tot_perc(),
            rank_de=self.rank_de(),
            unemployment_tot_perc_countries=self.unemployment_tot_perc_countries(),
            unemployment_tot_tot_eu=self.unemployment_tot_tot_eu(),
            unemployment_tot_perc_eu=self.unemployment_tot_perc_eu(),
            unemployment_tot_perc_ez=self.unemployment_tot_perc_ez(),
            eu_ez_comp=self.eu_ez_comp(),
            unemployment_tot_perc_countries_highest=self.unemployment_tot_perc_countries_highest(),
            unemployment_lt25_perc_eu=self.unemployment_lt25_perc_eu(),
            unemployment_lt25_perc_eu_rel=self.unemployment_lt25_perc_eu_rel(),
            unemployment_lt25_perc_countries_lowest=self.unemployment_lt25_perc_countries_lowest(),
            unemployment_lt25_perc_countries_highest=self.unemployment_lt25_perc_countries_highest(),
            countries_no_lt25=self.countries_no_lt25(),
            nbsp=u.NBSP,
        )

        return text
