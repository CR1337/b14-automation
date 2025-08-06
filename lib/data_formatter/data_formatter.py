from __future__ import annotations

from typing import Any

import pandas as pd


class DataFormatter:
    """
    Der `DataFormatter` kann einzelne numerische Werte oder ganze Spalten eines
    pandas.DataFrame formatieren. Es lassen sich Dezimal- und Tausender-
    Trennzeichen, die Anzahl der Dezimalstellen und ein Multiplier angeben.
    Der Wert wird einfach mit dem Multiplier multipliziert.
    """

    
    # Das sind die voreingestellten Dezimal- und Tausender-Trennzeichen
    # für Deutsch und Englisch.
    DECIMAL_SEPARATOR_DE: str = ","
    DECIMAL_SEPARATOR_EN: str = "."
    THOUSANDS_SEPARATOR_DE: str = "\u00a0"
    THOUSANDS_SEPARATOR_EN: str = ","

    @classmethod
    def german(
        cls, multiplier: float = 1.0, decimal_places: int = 2
    ) -> DataFormatter:
        """
        Gibt einen neuen `DataFormatter` zurück, der deutsche Trennzeichen 
        verwendet. Der Multiplier und die Dezimalstellen lassen sich angeben.
        """
        return cls(
            cls.DECIMAL_SEPARATOR_DE,
            cls.THOUSANDS_SEPARATOR_DE,
            multiplier,
            decimal_places
        )

    @classmethod
    def english(
        cls, multiplier: float = 1.0, decimal_places: int = 2
    ) -> DataFormatter:
        """
        Gibt einen neuen `DataFormatter` zurück, der englische Trennzeichen 
        verwendet. Der Multiplier und die Dezimalstellen lassen sich angeben.
        """
        return cls(
            cls.DECIMAL_SEPARATOR_EN,
            cls.THOUSANDS_SEPARATOR_EN,
            multiplier,
            decimal_places
        )

    _decimal_separator: str
    _thousands_separator: str
    _multiplier: float
    _decimal_places: int

    def __init__(
        self,
        decimal_separator: str,
        thousands_separator: str,
        multiplier: float = 1.0,
        decimal_places: int = 2
    ):
        """
        Gibt einen neuen `DataFormatter` zurück. Es müssen die zu verwendenden
        Trennzeichen, und optional ein Multiplier und die Dezimalstellen 
        engegeben werden.
        """
        self._decimal_separator = decimal_separator
        self._thousands_separator = thousands_separator
        self._multiplier = multiplier
        self._decimal_places = decimal_places

    def _format_function(self, value: Any) -> str:
        """
        Diese Funktion nimmt einen Wert entgegen und gibt ihn formatiert zurück.
        """
        try:
            # Wenn der Wert ein float ist oder sich in diesen umwandeln lässt,
            # wandle ihn in einen float um und multipliziere ihn mit dem
            # Multiplier
            value = float(value) * self._multiplier
        except ValueError:
            # Ansonsten lässt sich der Wert nicht formatieren und wird
            # unverändert zurückgegeben.
            return value
            
        # Dieser String gibt vor, wie der Wert zu formatieren ist. Als Dezimal-
        # trenner wird hier zunächst immer ein . und als Tausendertrenner
        # immer ein , verwendet. Außerdem wird hier die Anzahl der Dezimal-
        # stellen festgelegt
        format_string = f"{{:,.{self._decimal_places}f}}"
        
        # Dann wird der Wert entsprechend dem Format formatiert
        formatted_string = format_string.format(value)
        
        # Jetzt werden . und , durch die Platzhalter <d> und <t> ersetzt.
        formatted_string = formatted_string.replace(",", "<t>")
        formatted_string = formatted_string.replace(".", "<d>")
        
        # Dann werden die Platzhalter durch die egentlichen Zeichen ersetzt.
        formatted_string = formatted_string.replace(
            "<t>", self._thousands_separator
        )
        formatted_string = formatted_string.replace(
            "<d>", self._decimal_separator
        )
        
        return formatted_string

    def format_value(self, value: Any) -> str:
        """
        Diese Funktion nimmt einen Wert entgegen und gibt ihn formatiert zurück.
        """
        return self._format_function(value)

    def format_column(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Diese Funktion nimmt ein pandas.DataFrame und einen Spaltennamen
        entgegen und formatiert jeden Wert in der angegebenen Spalte. Das
        veränderte DataFrame wird zurückgegeben.
        """
        copy = data.copy()
        copy[column] = copy[column].apply(self._format_function)
        return copy

    @property
    def decimal_separator(self) -> str:
        """
        Gibt das verwendete Dezimaltrennzeichen zurück.
        """
        return self._decimal_separator

    @property
    def thousands_separator(self) -> str:
        """
        Gibt das verwendete Tausendertrennzeichen zurück.
        """
        return self._thousands_separator

    @property
    def multiplier(self) -> float:
        """
        Gibt den verwendeten Multiplier zurück.
        """
        return self._multiplier

    @property
    def decimal_places(self) -> int:
        """
        Gibt die verwendete Anzahl der Dezimalstellen zurück.
        """
        return self._decimal_places

