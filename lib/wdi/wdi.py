import wbwdi as wb
from enum import Enum
import pandas as pd
from typing import List
import polars as pl
from datetime import datetime
from itertools import product
import time


class Frequency(Enum):
    ANNUAL = "annual"
    MONTH = "month"
    QUARTER = "quarter"


class Wdi:

    YEAR_RANGE_SIZE: int = 5
    
    @classmethod
    def get(
        cls,
        indicators: List[str] | str, 
        start_year: int, 
        entities: List[str] | str = "all", 
        end_year: int = 0, 
        frequency: Frequency = Frequency.ANNUAL,
        verbose: bool = False
    ) -> pd.DataFrame:
        if isinstance(indicators, str):
            indicators = [indicators]

        end_year = end_year or datetime.today().year

        year_ranges = (
            (y, min(y + cls.YEAR_RANGE_SIZE, end_year))
            for y in range(start_year, end_year + 1, cls.YEAR_RANGE_SIZE)
        )
        year_ranges = (
            r for r in year_ranges
            if len(r) == 2 and r[0] != r[1]
        )
        dataframes = []

        for indicator, (start, end) in product(indicators, year_ranges):
            if verbose:
                print(f"Loading {indicator} for {start} - {end} ...")
            df = wb.wdi_get(
                entities=entities,
                indicators=[indicator],
                start_year=start,
                end_year=end,
                frequency=frequency.value,
                progress=False
            )
            assert isinstance(df, pl.DataFrame)
            dataframes.append(df.to_pandas())
            time.sleep(3)

        result = pd.concat(dataframes, ignore_index=True)

        return result


if __name__ == "__main__":
    df = Wdi.get(
        entities="all",
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
    print(df)