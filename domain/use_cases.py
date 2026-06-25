import logging
import os
from typing import Dict, Tuple

import pandas as pd

# ==============================================================================
# PRINCIPIO DE INVERSIÓN DE DEPENDENCIAS (DIP) y CLEAN ARCHITECTURE
# ==============================================================================
# Quitamos las importaciones directas de la capa de aplicación (transformer, validator)
# y de configuración. En su lugar, el dominio solo importa puertos (abstracciones)
# de domain.ports y excepciones del dominio.
# ==============================================================================
from domain.exceptions import ApiCaidaError, DatosNoEncontradosError
from domain.ports import (
    DataTransformerPort,
    DataValidatorPort,
    GetIndicatorsQuery,
    IndicatorReader,
    IndicatorSource,
    IndicatorWriter,
    PopulateDatabaseCommand,
)

logger = logging.getLogger("populate_db")


class GetIndicatorsUseCase(GetIndicatorsQuery):
    """
    Caso de uso para consultar indicadores nacionales.
    Aplica DIP al depender de puertos e ISP al depender solo de IndicatorReader.
    Aplica OCP al inyectar los indicadores y país por constructor en lugar de hardcodear.
    """
    def __init__(
        self,
        api_source: IndicatorSource,
        db_repo: IndicatorReader,          # ISP: Solo dependemos de lectura
        transformer: DataTransformerPort, # DIP: Dependemos del puerto del transformer
        indicators: Dict[str, str],        # OCP: Parámetro inyectado
        country: str,                      # OCP: Parámetro inyectado
    ):
        self._api = api_source
        self._repo = db_repo
        self._transformer = transformer
        self._indicators = indicators
        self._country = country

    def execute(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        anio_actual = pd.Timestamp.now().year
        anios_api = range(anio_actual - 16, anio_actual)

        try:
            # Consulta a la API externa
            raw = self._api.fetch_data(
                list(self._indicators.keys()), self._country, anios_api
            )
            return self._transformer.process_api_data(raw, self._indicators)
        except ApiCaidaError:
            try:
                # LSP: El repositorio SQLite ahora traduce sus errores de infraestructura y
                # lanza DatosNoEncontradosError. El caso de uso solo tiene que tratar con esta
                # excepción semántica del dominio.
                df = self._repo.load_data()
                return self._transformer.process_db_data(df)
            except DatosNoEncontradosError as e:
                # Mensaje de ayuda si no hay datos en absoluto
                raise DatosNoEncontradosError(
                    f"No hay conexion a internet ni base de datos local.\n\n"
                    f"**Paso requerido:** Ejecute el siguiente comando en la terminal "
                    f"para crear la base de datos local:\n\n"
                    f"```\npython populate_db.py\n```\n\n"
                    f"*(Requiere conexion a internet para descargar los datos del Banco Mundial xd)*"
                ) from e


class PopulateDatabaseUseCase(PopulateDatabaseCommand):
    """
    Caso de uso para sincronizar y poblar la base de datos.
    Aplica DIP al depender de puertos (source, repo, transformer, validator)
    e ISP al depender exclusivamente de la interfaz de escritura IndicatorWriter.
    Aplica OCP al recibir toda su configuración en el constructor.
    """
    def __init__(
        self,
        source: IndicatorSource,
        repo: IndicatorWriter,             # ISP: Solo dependemos de escritura y administración
        transformer: DataTransformerPort, # DIP: Dependemos de puertos
        validator: DataValidatorPort,     # DIP: Dependemos de puertos
        indicators: Dict[str, str],        # OCP: Inyección de configuración
        country: str,                      # OCP: Inyección de configuración
        db_name: str,                      # OCP: Inyección de configuración
        schema_file: str,                  # OCP: Inyección de configuración
        anios_historia: int,               # OCP: Inyección de configuración
        rangos_validos: Dict,              # OCP: Inyección de configuración
    ):
        self._source = source
        self._repo = repo
        self._transformer = transformer
        self._validator = validator
        self._indicators = indicators
        self._country = country
        self._db_name = db_name
        self._schema_file = schema_file
        self._anios_historia = anios_historia
        self._rangos_validos = rangos_validos

    def execute(self) -> None:
        logger.info("Iniciando inicializacion y sincronizacion de base de datos...")
        try:
            self._repo.connect(self._db_name)
            schema_path = os.environ.get("WORLDBANK_SCHEMA", self._schema_file)
            self._repo.execute_schema(schema_path)
            self._repo.save_indicators(self._indicators)

            anio_actual = pd.Timestamp.now().year
            anios = range(anio_actual - self._anios_historia, anio_actual + 1)

            df = self._source.fetch_data(
                list(self._indicators.keys()), self._country, anios
            )
            df_long = self._transformer.transform_populate(df)
            df_long = self._validator.validate(df_long, self._rangos_validos)
            registros = self._transformer.to_records(df_long)
            self._repo.save_values(registros)
            logger.info("Sincronizacion finalizada exitosamente.")
        except Exception:
            self._repo.rollback()
            raise
        finally:
            self._repo.close()
            logger.info("Conexion cerrada.")

