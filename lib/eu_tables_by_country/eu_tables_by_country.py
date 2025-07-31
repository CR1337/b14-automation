from typing import Any, Dict, List
import pandas as pd
from datetime import datetime as dt
import json
import os
import time
from requests import ConnectionError
from itertools import count

from lib.eurostat.eurostat_api.dataset import EurostatDataset
from lib.eurostat.eurostat_api.filters import TimePeriodFilter, DimensionFilter
from lib.data_formatter.data_formatter import DataFormatter
from lib.table_builder.table_builder import TableBuilder


LANGUAGE: str = 'en'

MIN_YEAR: str = "1990"
MIN_FILL_LEVEL: float = 0.5

SLEEP_BETWEEN_REQUESTS: float = 10.0  # s

EU_COUNTRIES: List[str] = [
    "BE", "BG", "DK", "DE", "EE", "FI",
    "FR", "EL", "IE", "IT", "HR", "LV",
    "LT", "LU", "MT", "NL", "AT", "PL",
    "PT", "RO", "SE", "SK", "SI", "ES",
    "CZ", "HU", "CY"
]
EU_CANDIDATE_COUNTRIES: List[str] = [
    "AL", "ME", "MK", "RS", "TR"
]
EFTA_COUNTRIES: List[str] = [
    "IS", "LI", "NO", "CH"
]

UNAVAILABLE_TEXTS: Dict[str, str] = {
    'de': "- -- Nichts vorhanden",
    'en': "- -- No figures or magnitude zero"
}

CONFIDENTIAL_TEXTS: Dict[str, str] = {
    'de': ". -- Zahlenwert unbekannt oder geheim zu halten",
    'en': ". -- Numerical value unknown or confidential"
}

with open(
    os.path.join("lib", "eu_tables_by_country", "data", "local_data.json"), 'r', encoding='utf-8'
) as file:
    content = json.load(file)
    CAPITALS: Dict[str, Dict[str, str]] = content['capitals']
    CURRENCIES: Dict[str, Dict[str, str]] = content['currencies']
    COUNTRY_NAMES: Dict[str, Dict[str, str]] = content['country_names']
    del content


def accumulate_data(
    dataset_definitions: Dict[str, Dict[str, str | Dict[str, str]]]
) -> Dict[str, EurostatDataset]:
    data = {}

    for data_key, definition in dataset_definitions.items():
        for _ in count(start=1):
            try:
                assert isinstance(definition['dataset_id'], str)
                dataset = EurostatDataset(definition['dataset_id'], LANGUAGE)

                dimension_filter = DimensionFilter(dataset)
                assert isinstance(definition['dimension_values'], dict)
                for key, value in definition['dimension_values'].items():
                    dimension_filter.add_dimension_value(key, value)

                time_period_filter = TimePeriodFilter(dataset)
                time_period_filter.add(
                    TimePeriodFilter.Operators.GREATER_OR_EQUALS, MIN_YEAR
                )

                dataset.request_data()

                data[data_key] = dataset
            except ConnectionError:
                pass
            else:
                break

            time.sleep(SLEEP_BETWEEN_REQUESTS)

    return data

def build_local_row(
    data: Dict[str, Dict[str, str]],
    country_code: str,
    other_country_code: str | None,
    value: str,
    index: List[str]
) -> pd.DataFrame:
    if other_country_code is None:
        rows = [
            str(dt.now().year),
            data[country_code][LANGUAGE],
            value
        ]
    else:
        rows = [
            str(dt.now().year),
            data[country_code][LANGUAGE],
            data[other_country_code][LANGUAGE],
            value
        ]
    return pd.DataFrame(
        rows,
        index=index,
        columns=['observation']
    )

def build_row_data(
    key: str,
    country_code: str,
    other_country_code: str | None,
    specification: Dict[str, Dict[str, Any]],
    data: Dict[str, EurostatDataset]
) -> pd.DataFrame:
    multiplier = specification.get('multiplier', 1.0)
    decimal_places = specification.get('decimal_places', 0)
    assert isinstance(multiplier, float)
    assert isinstance(decimal_places, int)
    formatter = (
        DataFormatter.german(multiplier, decimal_places)
        if LANGUAGE == 'de'
        else DataFormatter.english(multiplier, decimal_places)
    )

    if other_country_code is None:
        index = ["year", country_code, "EU27_2020"]
    else:
        index = ["year", country_code, other_country_code, "EU27_2020"]

    if specification['type'] == 'local':
        if key == 'capital':
            return build_local_row(
                CAPITALS,
                country_code,
                other_country_code,
                UNAVAILABLE_TEXTS[LANGUAGE],
                index
            )
        elif key == 'currency':
            return build_local_row(
                CURRENCIES,
                country_code,
                other_country_code,
                UNAVAILABLE_TEXTS[LANGUAGE],
                index
            )

    elif specification['type'] in ('data', 'geo_special'):
        is_geo_special = specification['type'] == 'geo_special'

        assert isinstance(specification['key'], str)
        dataset = data[specification['key']]
        time = dataset.data.get_latest_time_value_with(MIN_FILL_LEVEL, {})
        df = dataset.data.dataframe
        df = df[df['time'] == time]

        if is_geo_special:
            assert isinstance(specification['special_key'], str)
            special_dataset = data[specification['special_key']]
            special_time = special_dataset.data.get_latest_time_value_with(MIN_FILL_LEVEL, {})
            if int(time) > int(special_time):
                time = special_time
            special_df = special_dataset.data.dataframe
            special_df = special_df[special_df['time'] == time]
        else:
            special_df = pd.DataFrame()

        values = []
        for geo in index[1:]:
            try:
                if is_geo_special and geo == specification.get('special_geo'):
                    status = special_df[special_df['geo'] == geo]['status'].iat[0]
                else:
                    status = df[df['geo'] == geo]['status'].iat[0]
            except IndexError:
                values.append(UNAVAILABLE_TEXTS[LANGUAGE])
                continue

            if 'c' in status:
                values.append(CONFIDENTIAL_TEXTS[LANGUAGE])
                continue

            try:
                if is_geo_special and geo == specification.get('special_geo'):
                    value = special_df[special_df['geo'] == geo]['observation'].iat[0]
                else:
                    value = df[df['geo'] == geo]['observation'].iat[0]
            except IndexError:
                values.append(UNAVAILABLE_TEXTS[LANGUAGE])
                continue

            try:
                float(value)
            except ValueError:
                values.append(UNAVAILABLE_TEXTS[LANGUAGE])
            else:
                values.append(formatter.format_value(value))

        return pd.DataFrame(
            [time, *values],
            index=index,
            columns=['observation']
        )

    elif specification['type'] == 'ratio':
        dataset1 = data[specification['data'][0]['key']]  # type: ignore
        dataset2 = data[specification['data'][1]['key']]  # type: ignore

        time1 = dataset1.data.get_latest_time_value_with(MIN_FILL_LEVEL, {})
        if specification['data'][1]['time'] == 'other':  # type: ignore
            time2 = time1
        else:
            time2 = specification['data'][1]['time']  # type: ignore

        df1 = dataset1.data.dataframe
        df2 = dataset2.data.dataframe
        df1 = df1[df1['time'] == time1]
        df2 = df2[df2['time'] == time2]

        values = []
        for geo in index[1:]:
            try:
                status1 = df1[df1['geo'] == geo]['status'].iat[0]
                if 'c' in status1:
                    values.append(CONFIDENTIAL_TEXTS[LANGUAGE])
                    continue
            except IndexError:
                values.append(UNAVAILABLE_TEXTS[LANGUAGE])
                continue

            try:
                status2= df2[df2['geo'] == geo]['status'].iat[0]
                if 'c' in status2:
                    values.append(CONFIDENTIAL_TEXTS[LANGUAGE])
                    continue
            except IndexError:
                values.append(UNAVAILABLE_TEXTS[LANGUAGE])
                continue

            try:
                value1 = df1[df1['geo'] == geo]['observation'].iat[0]
                value2 = df2[df2['geo'] == geo]['observation'].iat[0]
            except IndexError:
                values.append(UNAVAILABLE_TEXTS[LANGUAGE])
                continue

            try:
                float(value1)
                float(value2)
            except ValueError:
                values.append(UNAVAILABLE_TEXTS[LANGUAGE])
            else:
                value = float(value1) / float(value2)
                values.append(formatter.format_value(value))

        return pd.DataFrame(
            [time1, *values],
            index=index,
            columns=['observation']
        )
    
    else:
        raise ValueError(f"Unexpected type: {specification['type']}")

def accumulate_table_data(row_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    df = pd.DataFrame()
    for key, row_df in row_data.items():
        df[key] = row_df['observation']
    return df

def build_table(
    table_data: pd.DataFrame,
    table_filename: str,
    localization_filename: str,
    variables: Dict[str, str],
    language: str
) -> bytes:
    table_data['empty_subheader'] = ""
    table_builder = TableBuilder(
        table_data, table_filename, localization_filename,
        variables=variables
    )
    return table_builder.build(language=language)

def build_table_set(
    country_codes: List[str],
    table_filename: str,
    localization_filename: str,
    specifications: Dict[str, Dict[str, Any]],
    data: Dict[str, EurostatDataset],
    language: str
) -> Dict[str, bytes]:
    result = {}
    for country_code in country_codes:
        other_country_code = None if country_code == 'DE' else 'DE'
        row_data = {
            key: build_row_data(
                key, country_code, other_country_code, specification, data
            )
            for key, specification in specifications.items()
        }
        table_data = accumulate_table_data(row_data)
        country_name = COUNTRY_NAMES[country_code][LANGUAGE]
        other_country_name = (
            COUNTRY_NAMES[other_country_code][LANGUAGE]
            if other_country_code in COUNTRY_NAMES
            else None
        )
        variables = {
            'header_country': country_name,
            'header_other_country': other_country_name
        }
        result[country_code] = build_table(
            table_data, table_filename, localization_filename,
            variables, language
        )
    return result


def build_tables(language: str) -> Dict[str, Dict[str, bytes]]:
    data_directory = os.path.join("lib", "eu_tables_by_country", "data")
    definitions_filename = os.path.join(data_directory, "dataset_definitions.json")
    row_specifications_filename = os.path.join(data_directory, "row_specifications.json")
    with open(definitions_filename, 'r') as file:
        definition = json.load(file)
    data = accumulate_data(definition)
    with open(row_specifications_filename, 'r') as file:
        row_specifications = json.load(file)
    
    tables = {}
    for region_code, country_codes in (('eu', EU_COUNTRIES), ('eu_cand', EU_CANDIDATE_COUNTRIES), ('efta', EFTA_COUNTRIES)):
        table_filename = os.path.join(data_directory, f"{region_code}_layout.json")
        localization_filename = os.path.join(data_directory, f"{region_code}_localization.json")
        table_set = build_table_set(
            country_codes=country_codes,
            table_filename=table_filename,
            localization_filename=localization_filename,
            specifications=row_specifications,
            data=data,
            language=language
        )
        tables[region_code] = table_set
    
    return tables