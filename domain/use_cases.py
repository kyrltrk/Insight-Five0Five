import logging
import os
from typing import Tuple

import pandas as pd

from application.transformer import DataTransformer
from application.validator import DataValidator
from config.settings import (
    ANIOS_HISTORIA,
    DB_NAME,
    INDICATORS,
    PAIS,
    RANGOS_VALIDOS,
    SCHEMA_FILE,
)
from domain.exceptions import ApiCaidaError, DatosNoEncontradosError
from domain.ports import (
    GetIndicatorsQuery,
    IndicatorRepository,
    IndicatorSource,
    PopulateDatabaseCommand,
)

logger = logging.getLogger("populate_db")


class GetIndicatorsUseCase(GetIndicatorsQuery):
    def __init__(
        self,
        api_source: IndicatorSource,
        db_repo: IndicatorRepository,
        transformer: DataTransformer,
    ):
        self._api = api_source
        self._repo = db_repo
        self._transformer = transformer

    def execute(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        anio_actual = pd.Timestamp.now().year
        anios_api = range(anio_actual - 16, anio_actual)

        try:
            raw = self._api.fetch_data(
                list(INDICATORS.keys()), PAIS, anios_api
            )
            return self._transformer.process_api_data(raw, INDICATORS)
        except ApiCaidaError:
            try:
                df = self._repo.load_data()
                if df.empty:
                    raise DatosNoEncontradosError(
                        "La base de datos local esta vacia."
                    )
                return self._transformer.process_db_data(df)
            except (FileNotFoundError, ValueError) as e:
                raise DatosNoEncontradosError(
                    f"No hay conexion a internet ni base de datos local.\n\n"
                    f"**Paso requerido:** Ejecute el siguiente comando en la terminal "
                    f"para crear la base de datos local:\n\n"
                    f"```\npython populate_db.py\n```\n\n"
                    f"*(Requiere conexion a internet para descargar los datos del Banco Mundial xd)*"
                ) from e


class PopulateDatabaseUseCase(PopulateDatabaseCommand):
    def __init__(
        self,
        source: IndicatorSource,
        repo: IndicatorRepository,
        transformer: DataTransformer,
        validator: DataValidator,
    ):
        self._source = source
        self._repo = repo
        self._transformer = transformer
        self._validator = validator

    def execute(self) -> None:
        logger.info("Iniciando inicializacion y sincronizacion de base de datos...")
        try:
            self._repo.connect(DB_NAME)
            schema_path = os.environ.get("WORLDBANK_SCHEMA", SCHEMA_FILE)
            self._repo.execute_schema(schema_path)
            self._repo.save_indicators(INDICATORS)

            anio_actual = pd.Timestamp.now().year
            anios = range(anio_actual - ANIOS_HISTORIA, anio_actual + 1)

            df = self._source.fetch_data(
                list(INDICATORS.keys()), PAIS, anios
            )
            df_long = self._transformer.transform_populate(df)
            df_long = self._validator.validate(df_long, RANGOS_VALIDOS)
            registros = self._transformer.to_records(df_long)
            self._repo.save_values(registros)
            logger.info("Sincronizacion finalizada exitosamente.")
        except Exception:
            self._repo.rollback()
            raise
        finally:
            self._repo.close()
            logger.info("Conexion cerrada.")
