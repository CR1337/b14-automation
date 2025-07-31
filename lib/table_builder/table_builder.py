import io
import json
import math
from typing import Any, Dict, List, Tuple, Callable

import pandas as pd
import xlsxwriter as xls


class TableBuilder:

    _data: pd.DataFrame
    _table_data: Dict[str, Any]
    _localization_data: Dict[str, Dict[str, str]]
    _variables: Dict[str, str]

    _decimal_separator: str
    _thousands_separator: str
    _none_value: str
    _format_function: Callable[[Any], str]

    _language: str

    _workbook: Any
    _worksheet: Any
    _modified_data: Dict[str, pd.DataFrame]

    def __init__(
        self,
        data: pd.DataFrame,
        table_filename: str,
        localization_filename: str | None = None,
        variables: Dict[str, str] | None = None,
        decimal_separator: str = ",",
        thousands_separator: str = ".",
        none_value: str = "-",
        format_function: Callable[[Any], str] = lambda v: str(v)
    ):
        self._data = data
        with open(table_filename, 'r') as file:
            self._table_data = json.load(file)
        if localization_filename:
            with open(localization_filename, 'r') as file:
                self._localization_data = json.load(file)
        else:
            self._localization_data = {}
        self._variables = variables if variables else {}
        self._decimal_separator = decimal_separator
        self._thousands_separator = thousands_separator
        self._none_value = none_value
        self._format_function = format_function

    def build(
        self,
        language: str
    ):
        buffer = io.BytesIO()
        self._workbook = xls.Workbook(buffer, {'in_memory': True})
        self._worksheet = self._workbook.add_worksheet()

        self._language = language

        _, header_height = self._build_header(self._table_data['header'], 0, 0)
        self._build_elements(header_height)

        self._workbook.close()
        buffer.seek(0)
        return buffer.getvalue()

    def write_cell(self, x: int, y: int, value: str):
        value = self._replace_value(value)
        if not isinstance(value, str):
            if value is None:
                value = self._none_value
            elif math.isnan(value):
                value = self._none_value
        cell = f"{self._index_to_column(x)}{y + 1}"
        self._worksheet.write(cell, value)

    def _index_to_column(self, index: int) -> str:
        column = ''
        while index >= 0:
            column = chr(index % 26 + ord('A')) + column
            index = index // 26 - 1
        return column

    def _replace_value(self, value: Any):
        if str(value).startswith("$[") and str(value).endswith("]"):
            return self._localization_data[value[2:-1]][self._language]
        elif str(value).startswith("${") and str(value).endswith("}"):
            return self._variables[value[2:-1]]
        else:
            return value

    def _build_header(
        self, subheader: Dict[str, Any], x: int, y: int
    ) -> Tuple[int, int]:
        if 'ifdefined' in subheader:
            if self._variables.get(subheader['ifdefined']) is None:
                return x - 1, y
        if (text := subheader['text']) is not None:
            self.write_cell(x, y, text)
            y += 1
        max_height = y
        for subsubheader in subheader['header']:
            x, height = self._build_header(subsubheader, x, y)
            x += 1
            max_height = max(max_height, height)
        if len(subheader['header']) > 0:
            x -= 1
        return x, max_height

    def _build_elements(self, y: int):
        for element in self._table_data['elements']:
            if element['type'] == 'columns':
                y = self._build_columns(element['columns'], y)
            elif element['type'] == 'rows':
                y = self._build_rows(element['rows'], y)

    def _prepare_data(
        self, key: str, fixed_values: Dict[str, str]
    ) -> List[str]:
        df = self._data[key].to_frame()
        for column_name, value in fixed_values.items():
            df = df.loc[df[column_name] == value]
        columns_to_display = df.columns.difference(
            list(fixed_values.keys())
        ).to_list()
        if len(columns_to_display) == 0:
            raise ValueError("No unfixed column!")
        elif len(columns_to_display) > 1:
            raise ValueError(
                f"Too many unfixed columns: {len(columns_to_display)}!"
            )
        return df[columns_to_display[0]].to_list()

    def _value_from_string(self, value: str) -> float | None:
        value = value.replace(self._thousands_separator, "")
        value = value.replace(self._decimal_separator, ".")
        try:
            return float(value)
        except ValueError:
            return None

    def _compute_ratio(self, value1: str, value2: str) -> str:
        value1_f = self._value_from_string(value1)
        value2_f = self._value_from_string(value2)
        if None in (value1_f, value2_f):
            return self._none_value
        assert value1_f is not None and value2_f is not None
        ratio = value1_f / value2_f
        return self._format_function(ratio)

    def _prepare_ratio(
        self, key1: str, key2: str,
        fixed_values1: Dict[str, str], fixed_values2: Dict[str, str]
    ):
        data1 = self._prepare_data(key1, fixed_values1)
        data2 = self._prepare_data(key2, fixed_values2)
        return [self._compute_ratio(v1, v2) for v1, v2 in zip(data1, data2)]

    def _build_columns(self, columns: List[Dict[str, Any]], y: int) -> int:
        max_height = 0
        for x, column in enumerate(columns):
            max_height = max(
                self._build_column(column, x, y),
                max_height
            )
        return max_height

    def _build_column(self, column: Dict[str, Any], x: int, y: int) -> int:
        if column['key'] == '__RATIO__':
            if 'fixed_values1' not in column:
                column['fixed_values1'] = {}
            if 'fixed_values2' not in column:
                column['fixed_values2'] = {}
            data = self._prepare_ratio(
                column['key1'], column['key2'],
                column['fixed_values1'], column['fixed_values2']
            )
        else:
            if 'fixed_values' not in column:
                column['fixed_values'] = {}
            data = self._prepare_data(column['key'], column['fixed_values'])
        for y_offset, value in enumerate(data):
            self.write_cell(x, y + y_offset, value)
        return y + len(data)

    def _build_rows(self, rows: List[Dict[str, Any]], y: int) -> int:
        for y_ in range(y, y + len(rows)):
            self._build_row(rows[y_ - y], y_)
        return y + len(rows)

    def _build_row(self, row: Dict[str, Any], y: int) -> int:
        if 'fixed_values' not in row:
            row['fixed_values'] = {}
        data = self._prepare_data(row['key'], row['fixed_values'])
        x_offset = 0
            
        if row['front'] is not None:
            front = row['front']
            if not isinstance(front, list):
                front = [front]
            for value in front:
                self.write_cell(x_offset, y, value)
                x_offset += 1
                
        for x, value in enumerate(data):
            self.write_cell(x + x_offset, y, value)
        return y + 1