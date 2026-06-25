import os
import sqlite3
from typing import Dict, List, Optional, Tuple

import pandas as pd

# ==============================================================================
# PRINCIPIOS SOLID: ISP, SRP y LSP
# ==============================================================================
# 1. ISP: Implementa IndicatorRepository (que hereda de IndicatorReader e IndicatorWriter).
# 2. SRP: Centraliza la ruta de la base de datos a través de la propiedad de instancia
#    self._db_path para evitar inconsistencias en load_data.
# 3. LSP: Captura errores internos de infraestructura (sqlite3.Error, FileNotFoundError)
#    y los traduce a excepciones semánticas de dominio (DatosNoEncontradosError).
# ==============================================================================
from domain.exceptions import DatosNoEncontradosError, EsquemaNoEncontradoError
from domain.ports import IndicatorRepository


class SQLiteRepository(IndicatorRepository):
    def __init__(self, db_path: str = "worldbank.db"):
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self, db_path: str) -> None:
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA foreign_keys = ON")

    def execute_schema(self, schema_path: str) -> None:
        if not os.path.exists(schema_path):
            raise EsquemaNoEncontradoError(
                f"No se encontro el archivo de esquema {schema_path}."
            )
        with open(schema_path, "r", encoding="utf-8") as f:
            esquema = f.read()
        self._conn.executescript(esquema)

    def save_indicators(self, indicators: Dict[str, str]) -> int:
        cursor = self._conn.cursor()
        cursor.executemany(
            "INSERT OR IGNORE INTO indicadores (codigo, nombre) VALUES (?, ?)",
            list(indicators.items()),
        )
        self._conn.commit()
        return len(indicators)

    def save_values(
        self, records: List[Tuple[str, str, int, Optional[float]]]
    ) -> int:
        cursor = self._conn.cursor()
        cursor.executemany(
            "INSERT OR REPLACE INTO valores (pais, indicador_codigo, anio, valor) "
            "VALUES (?, ?, ?, ?)",
            records,
        )
        self._conn.commit()
        return len(records)

    def load_data(self) -> pd.DataFrame:
        # LSP: El cliente espera DatosNoEncontradosError, no FileNotFoundError ni sqlite3.Error.
        # Validamos la existencia del archivo de base de datos antes de realizar la consulta.
        if not os.path.exists(self._db_path):
            raise DatosNoEncontradosError(
                f"No hay conexion a internet ni base de datos local en '{self._db_path}'."
            )

        query = """
            SELECT v.pais AS economy,
                   v.indicador_codigo AS series,
                   v.anio AS Year,
                   v.valor AS Value,
                   i.nombre AS Indicator
            FROM valores v
            JOIN indicadores i ON v.indicador_codigo = i.codigo
            ORDER BY v.anio
        """
        
        try:
            # SRP: Usar la conexión activa si existe; de lo contrario, abrir y cerrar una temporal.
            if self._conn is not None:
                df = pd.read_sql_query(query, self._conn)
            else:
                conn = sqlite3.connect(self._db_path)
                try:
                    df = pd.read_sql_query(query, conn)
                finally:
                    conn.close()
        except sqlite3.Error as e:
            raise DatosNoEncontradosError(
                f"Error al realizar consulta SQL en base de datos local: {e}"
            )

        if df.empty:
            raise DatosNoEncontradosError("La base de datos local esta vacia.")

        return df

    def rollback(self) -> None:
        if self._conn:
            self._conn.rollback()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

