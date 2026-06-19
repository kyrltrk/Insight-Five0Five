from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from domain.exceptions import ApiCaidaError, DatosNoEncontradosError
from domain.ports import IndicatorRepository, IndicatorSource


class FakeSource(IndicatorSource):
    def __init__(self, data: Optional[pd.DataFrame] = None, should_fail: bool = False):
        self._data = data
        self._should_fail = should_fail
        self.call_count = 0

    def fetch_data(
        self, indicators: List[str], country: str, years: range
    ) -> pd.DataFrame:
        self.call_count += 1
        if self._should_fail:
            raise ApiCaidaError("API simulada caida")
        if self._data is not None:
            return self._data
        data = {
            "economy": [country] * 2,
            "series": indicators[:2],
        }
        for y in years:
            data[f"YR{y}"] = [np.nan] * 2
        return pd.DataFrame(data)


class FakeRepository(IndicatorRepository):
    def __init__(self, data: Optional[pd.DataFrame] = None):
        self._data = data
        self._saved_indicators: Dict[str, str] = {}
        self._saved_values: List[Tuple] = []
        self._connected = False
        self._was_connected = False
        self._schema_executed = False

    def connect(self, db_path: str) -> None:
        self._connected = True
        self._was_connected = True

    def execute_schema(self, schema_path: str) -> None:
        self._schema_executed = True

    def save_indicators(self, indicators: Dict[str, str]) -> int:
        self._saved_indicators = indicators
        return len(indicators)

    def save_values(self, records: List[Tuple]) -> int:
        self._saved_values = records
        return len(records)

    def load_data(self) -> pd.DataFrame:
        if self._data is None or self._data.empty:
            raise DatosNoEncontradosError("No hay datos en el repositorio simulado")
        return self._data

    def rollback(self) -> None:
        pass

    def close(self) -> None:
        self._connected = False
