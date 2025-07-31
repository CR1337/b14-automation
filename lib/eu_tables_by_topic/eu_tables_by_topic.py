# import warnings
# warnings.simplefilter(action='ignore')

from typing import Any, Dict, Tuple
import pandas as pd
import json
import math
import os

from lib.eurostat.eurostat_api.dataset import EurostatDataset
from lib.eurostat.eurostat_api.filters import TimePeriodFilter, DimensionFilter
from lib.data_formatter.data_formatter import DataFormatter
from lib.table_builder.table_builder import TableBuilder


# Pfade die in dieser Anwendung verwendet werden
TABLE_DATA_PATH: str = os.path.join("lib", "eu_tables_by_topic", "data")

# Ab diesem Jahr werden Daten abgerufen
MIN_YEAR: str = '1990'
# Ein Jahr muss 50 % der Daten zu Verfügung stellen, um ausgewählt zu werden
MIN_FILL_LEVEL: float = 0.5

# Texte, die angezeigt werden, wenn keine Daten vorhanden sind
UNAVAILABLE_TEXTS: Dict[str, str] = {
    'de': "- -- Nichts vorhanden",
    'en': "- -- No figures or magnitude zero"
}

# Texte, die angezeigt werden, wenn Daten geheim sind
CONFIDENTIAL_TEXTS: Dict[str, str] = {
    'de': ". -- Zahlenwert unbekannt oder geheim zu halten",
    'en': ". -- Numerical value unknown or confidential"
}

# Lesen von Staatennamen und der Anzeigereihenfolge der Staaten aus Dateien
with open(os.path.join(TABLE_DATA_PATH, "country_order.json"), 'r') as file:
  COUNTRY_ORDER = json.load(file)
with open(os.path.join(TABLE_DATA_PATH, "country_names.json"), 'r') as file:
  COUNTRY_NAMES = json.load(file)

def parse_specification(
    column_specification: Dict[str, Any], language: str
) -> Tuple[pd.DataFrame, str]:
    if column_specification.get('is_ratio', False):
        specifications = column_specification['specifications']
        ds1, time1 = prepare_dataframe(
            dataset_id=specifications[0]['dataset_id'],
            dimension_values=specifications[0]['dimension_values'],
            time=specifications[0].get('time', None),
            language=language
        )

        time2 = specifications[1].get('time', None)
        if time2 == 'same':
            time2 = time1

        ds2, time2 = prepare_dataframe(
            dataset_id=specifications[1]['dataset_id'],
            dimension_values=specifications[1]['dimension_values'],
            time=time2,
            language=language
        )

        df1 = ds1.data.dataframe
        df2 = ds2.data.dataframe
        df1 = df1[df1['time'] == time1]
        df2 = df2[df2['time'] == time2]
        df = build_ratio_dataframe(df1, df2, ds1)
        time = max(time1, time2)

    else:
        ds, time = prepare_dataframe(
            dataset_id=column_specification['dataset_id'],
            dimension_values=column_specification['dimension_values'],
            time=column_specification.get('time', None),
            language=language
        )

        df = ds.data.dataframe
        df = df[df['time'] == time]

    return df, time

def prepare_dataframe(
    dataset_id: str,
    dimension_values: Dict[str, str],
    time: str | None,
    language: str
) -> Tuple[EurostatDataset, str]:
    dataset = EurostatDataset(
        dataset_id=dataset_id,
        language=language
    )

    dimension_filter = DimensionFilter(dataset)
    for key, value in dimension_values.items():
      dimension_filter.add_dimension_value(key, value)

    time_period_filter = TimePeriodFilter(dataset)
    time_period_filter.add(TimePeriodFilter.Operators.GREATER_OR_EQUALS, MIN_YEAR)

    dataset.request_data()

    latest_time = dataset.data.get_latest_time_value_with(MIN_FILL_LEVEL, {})
    time = latest_time if time is None else time

    return dataset, time


def compute_ratio(row, dataset: EurostatDataset) -> float | str:
    value1 = row['observation_1']
    value2 = row['observation_2']
    try:
        return float(value1) / float(value2)
    except (ValueError, ZeroDivisionError, TypeError):
        return EurostatDataset.none_value  # type: ignore


def merge_status(row) -> str:
    status1 = row['status_1'] if isinstance(row['status_1'], str) else ""
    status2 = row['status_2'] if isinstance(row['status_2'], str) else ""
    return "".join(set(status1) | set(status2))


def build_ratio_dataframe(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    dataset: EurostatDataset
) -> pd.DataFrame:
    df = pd.merge(
        df1,
        df2,
        left_on='geo',
        right_on='geo',
        how='outer',
        suffixes=("_1", "_2")
    )
    df['observation'] = df.apply(compute_ratio, axis=1, args=(dataset,))
    df['status'] = df.apply(merge_status, axis=1)
    df['time'] = df.apply(lambda r: max(str(r['time_1']), str(r['time_2'])), axis=1)
    return df


def combine_dataframes(dfs: Dict[str, pd.DataFrame], language: str) -> pd.DataFrame:
    dataframe = pd.DataFrame()
    for idx, (key, df) in enumerate(dfs.items()):
        df = df[df['geo'].isin(COUNTRY_ORDER[language])].copy()
        if idx == 0:
            dataframe = df
        else:
            dataframe = pd.merge(
                dataframe,
                df,
                left_on='geo',
                right_on='geo',
                how='outer',
                suffixes=("", "")
            )

        dataframe[key] = dataframe['observation']
        dataframe[f"{key}_status"] = dataframe['status']
        dataframe = dataframe.drop(columns=['observation', 'status'])

    return dataframe


def sort_dataframe(df: pd.DataFrame, language: str) -> pd.DataFrame:
    sorter = COUNTRY_ORDER[language]
    sorter_index = dict(zip(sorter, range(len(sorter))))
    df['geo_rank'] = df['geo'].map(sorter_index)
    df = df.sort_values(['geo_rank'], ascending=[True])
    df = df.drop(columns=['geo_rank'])

    return df


def format_unavailable_row(row, key: str, status_key: str, language: str) -> str:
    value = row[key]
    status = row[status_key] if isinstance(row[status_key], str) else ""
    if 'c' in status:
        return CONFIDENTIAL_TEXTS[language]
    else:
        try:
            v = float(value)
        except ValueError:
            return UNAVAILABLE_TEXTS[language]
        else:
            if math.isnan(v):
                return UNAVAILABLE_TEXTS[language]
            else:
                return value


def format_dataframe(
    df: pd.DataFrame,
    column_specifications: Dict[str, Dict[str, Any]],
    language: str
) -> pd.DataFrame:
    df = df.replace({'geo': COUNTRY_NAMES[language]})

    for key, specification in column_specifications.items():
        status_key = f"{key}_status"
        df[key] = df.apply(format_unavailable_row, axis=1, args=(key, status_key, language))
        df = df.drop(columns=[status_key])

        multiplier = specification['multiplier']
        decimal_places = specification['decimal_places']
        formatter = (
            DataFormatter.german(multiplier, decimal_places)
            if language == 'de'
            else DataFormatter.english(multiplier, decimal_places)
        )
        df = formatter.format_column(df, key)

    return df


def build_table(
    table_filename: str,
    localization_filename: str,
    column_specifications: Dict[str, Dict[str, Any]],
    language: str
) -> bytes:
    """
    Nimmt eine Spaltenspezifikation und drei Dateinamen entgegen.

    `column_specification` gibt an, welche Daten die zu erstellende
    Tabelle enthalten soll.

    `table_filename` ist der Pfad zu der json-Datei welche die Format-
    informationen für die zu erstellende Tabelle enthält.

    `localization_filename` ist der Pfad zu der json-Datei, welche die
    Übersetzungen ins Deutsche und Englische enthält

    `output_filename` ist der Pfad zu der xlsx-Datei, welche die
    fertige Tabelle enthält.

    Nachdem die Funktion ausgeführt wurde, wurde eine xlsx-Datei erstellt,
    die die Tabelle enthält.
    """

    # Diese beiden Variablen werden mit den anzuzeigenden Daten (`dataframes`)
    # und weiteren variablen Werten (`variables`) gefüllt, die letztendlich
    # in der Tabelle enthalten sein sollen. Wie und wo genau diese angezeigt
    # werden, ist in der Datei `table_filename` festgelegt.
    dataframes, variables = {}, {}

    # Für jede Spalte werden:
    #   1. die Daten von Eurostat herunter geladen (`df`) und die späteste
    #      Zeit mit mindestens `MIN_FILL_LEVEL` einträgen (`time`) bestimmt.
    #   2. alle unnötigen Spalten (alle außer 'geo', 'observation', 'status')
    #      entfernt
    #   3. die einzelnen DataFrames unter dem in der Speifikation angegebenen
    #      Schlüssel abgelegt
    #   4. die Zeit (`time`) den Variablen hinzugefügt, sodass sie in der
    #      Tabelle angezeigt werden kann.
    for column_key, column_specification in column_specifications.items():
        df, time = parse_specification(column_specification, language)
        df = df[['geo', 'observation', 'status']]
        dataframes[column_key] = df
        variables[f"{column_key}_time"] = time

    # Die DataFrames werden dann zu einem kombiniert, nach der
    # vorgegebenen Staatenreihenfolge sortiert und dann die Werte formatiert.
    combined_df = combine_dataframes(dataframes, language)
    sorted_df = sort_dataframe(combined_df, language)
    formatted_df = format_dataframe(sorted_df, column_specifications, language)

    # Das formatierte DataFrame, die Dateien, welche die tabelle spezifizieren
    # und die Variablen werden einem neuen `TableBuilder`-Objekt übergeben.
    table_builder = TableBuilder(
        data=formatted_df,
        table_filename=table_filename,
        localization_filename=localization_filename,
        variables=variables
    )

    # Die Tabelle wird gebaut unter Angabe der Ausgabedatei und der zu
    # verwendenden Sprache.
    return table_builder.build(
        language=language
    )


def create_build_table_params(table_id: str, language: str) -> Tuple[str, str, Dict[str, Dict[str, Any]], str]:
    data_directory = os.path.join("lib", "eu_tables_by_topic", "data")
    layout_filename = os.path.join(data_directory, f"{table_id}_layout.json")
    localization_filename = os.path.join(data_directory, f"{table_id}_localization.json")
    specification_filename = os.path.join(data_directory, f"{table_id}_specification.json")
    with open(specification_filename, 'r') as file:
        specification = json.load(file)
    return layout_filename, localization_filename, specification, language


def build_tables(language: str) -> Dict[str, bytes]:
    return {
        table_id: build_table(*create_build_table_params(table_id, language))
        for table_id in [
            "allgemeines",
            "arbeitsmarkt",
            "aussenhandel",
            "bevoelkerung",
            "bildung",
            "gesundheit",
            "industrie",
            "landwirtschaft",
            "soziales",
            "umwelt",
            "verkehr",
            "wirtschaft",
            "wissenschaft"
        ]
    }