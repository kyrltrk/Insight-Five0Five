from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import pandas as pd

# ==============================================================================
# PRINCIPIO DE INVERSIÓN DE DEPENDENCIAS (DIP) e INTERFACE SEGREGATION (ISP)
# ==============================================================================
# Definimos puertos (interfaces abstractas) para que el dominio no dependa de
# detalles concretos de infraestructura o de la capa de aplicación.
# ==============================================================================

class IndicatorSource(ABC):
    """Puerto para la fuente externa de indicadores (API)."""
    @abstractmethod
    def fetch_data(
        self, indicators: List[str], country: str, years: range
    ) -> pd.DataFrame:
        ...


# ------------------------------------------------------------------------------
# INTERFACE SEGREGATION PRINCIPLE (ISP)
# Segregamos el puerto de persistencia en interfaces de lectura y escritura.
# Así, el caso de uso de consulta no depende de métodos de escritura.
# ------------------------------------------------------------------------------

class IndicatorReader(ABC):
    """Puerto segregado únicamente para lectura de indicadores (ISP)."""
    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        ...


class IndicatorWriter(ABC):
    """Puerto segregado únicamente para escritura y administración de base de datos (ISP)."""
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
    def rollback(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...


class IndicatorRepository(IndicatorReader, IndicatorWriter, ABC):
    """Interfaz unificada que hereda de ambos puertos para mantener compatibilidad."""
    pass


# ------------------------------------------------------------------------------
# DEPENDENCY INVERSION PRINCIPLE (DIP)
# Creamos puertos para el DataTransformer y DataValidator. Con esto evitamos
# que la capa de dominio importe directamente implementaciones de la capa de aplicación.
# ------------------------------------------------------------------------------

class DataTransformerPort(ABC):
    """Puerto que define las operaciones de transformación de datos (DIP)."""
    @abstractmethod
    def process_api_data(
        self, raw_df: pd.DataFrame, indicator_map: Dict[str, str]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        ...

    @abstractmethod
    def process_db_data(
        self, df_long: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        ...

    @abstractmethod
    def transform_populate(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        ...

    @abstractmethod
    def to_records(
        self, df_long: pd.DataFrame
    ) -> List[Tuple]:
        ...


class DataValidatorPort(ABC):
    """Puerto que define las operaciones de validación de datos (DIP)."""
    @abstractmethod
    def validate(
        self,
        df_long: pd.DataFrame,
        rangos: Dict[str, Tuple[Optional[float], Optional[float]]],
        anio_minimo: int = 1990,
        anio_maximo: Optional[int] = None,
    ) -> pd.DataFrame:
        ...


# ------------------------------------------------------------------------------
# SINGLE RESPONSIBILITY PRINCIPLE (SRP)
# Puerto para aislar la lógica de cálculo de anomalías matemáticas fuera de la UI.
# ------------------------------------------------------------------------------

class AnomalyDetectorPort(ABC):
    """Puerto para la detección estadística de anomalías (SRP)."""
    @abstractmethod
    def detect_anomalies(
        self, years: List[int], values: List[float], std_devs: float = 2.0
    ) -> List[Tuple[int, float]]:
        """Retorna una lista de tuplas (año, variación) identificadas como anomalías."""
        ...


class GetIndicatorsQuery(ABC):
    @abstractmethod
    def execute(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        ...


class PopulateDatabaseCommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        ...

