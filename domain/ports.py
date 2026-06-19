from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import pandas as pd


class IndicatorSource(ABC):
    @abstractmethod
    def fetch_data(
        self, indicators: List[str], country: str, years: range
    ) -> pd.DataFrame:
        ...


class IndicatorRepository(ABC):
    @abstractmethod
    def connect(self, db_path: str) -> None:
        ...

    @abstractmethod
    def execute_schema(self, schema_path: str) -> None:
        ...

    @abstractmethod
    def save_indicators(self, indicators: Dict[str, str]) -> int:
        ...

    @abstractmethod
    def save_values(self, records: List[Tuple]) -> int:
        ...

    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...


class GetIndicatorsQuery(ABC):
    @abstractmethod
    def execute(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        ...


class PopulateDatabaseCommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...
