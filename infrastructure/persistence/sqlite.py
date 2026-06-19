import os
import sqlite3
from typing import Dict, List, Optional, Tuple

import pandas as pd

from domain.exceptions import EsquemaNoEncontradoError
from domain.ports import IndicatorRepository


class SQLiteRepository(IndicatorRepository):
    def __init__(self):
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self, db_path: str) -> None:
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
        ruta_db = os.environ.get("WORLDBANK_DB", "worldbank.db")

        if not os.path.exists(ruta_db):
            raise FileNotFoundError(
                "No hay conexion a internet ni base de datos local."
            )

        conn = sqlite3.connect(ruta_db)
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
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            raise ValueError("La base de datos local esta vacia.")

        return df

    def rollback(self) -> None:
        if self._conn:
            self._conn.rollback()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
