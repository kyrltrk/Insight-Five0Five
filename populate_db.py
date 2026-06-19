import os
import sys
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

DB_NAME: str = os.environ.get("WORLDBANK_DB", "worldbank.db")
SCHEMA_FILE: str = os.environ.get("WORLDBANK_SCHEMA", "schema.sql")
PAIS: str = os.environ.get("WORLDBANK_PAIS", "NIC")
ANIOS_HISTORIA: int = int(os.environ.get("WORLDBANK_ANIOS", "30"))

INDICADORES: Dict[str, str] = {
    "IT.NET.USER.ZS": "Uso de Internet (%)",
    "BX.TRF.PWKR.DT.GD.ZS": "Remesas (% del PIB)",
    "EG.ELC.ACCS.ZS": "Acceso a Electricidad (%)",
    "SE.XPD.TOTL.GD.ZS": "Inversión en Educación (% PIB)",
    "SP.DYN.LE00.IN": "Esperanza de Vida (Años)",
    "SH.XPD.CHEX.GD.ZS": "Gasto en Salud (% PIB)",
    "FP.CPI.TOTL.ZG": "Inflación (% Anual)",
    "SL.UEM.TOTL.ZS": "Desempleo (%)",
}

RANGOS_VALIDOS: Dict[str, Tuple[Optional[float], Optional[float]]] = {
    "IT.NET.USER.ZS": (0, 100),
    "BX.TRF.PWKR.DT.GD.ZS": (0, 100),
    "EG.ELC.ACCS.ZS": (0, 100),
    "SE.XPD.TOTL.GD.ZS": (0, 100),
    "SP.DYN.LE00.IN": (20, 100),
    "SH.XPD.CHEX.GD.ZS": (0, 100),
    "FP.CPI.TOTL.ZG": (-50, 500),
    "SL.UEM.TOTL.ZS": (0, 100),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("populate_db")


def conectar_base_datos(ruta: str) -> sqlite3.Connection:
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")
    logger.info("Conexión establecida a %s", ruta)
    return conexion


def ejecutar_esquema(conexion: sqlite3.Connection, ruta_esquema: str) -> None:
    if not os.path.exists(ruta_esquema):
        raise FileNotFoundError(
            f"No se encontró el archivo de esquema {ruta_esquema}."
        )
    logger.info("Leyendo esquema desde %s...", ruta_esquema)
    with open(ruta_esquema, "r", encoding="utf-8") as f:
        esquema = f.read()
    conexion.executescript(esquema)
    logger.info("Esquema creado correctamente.")


def poblar_indicadores(
    conexion: sqlite3.Connection, indicadores: Dict[str, str]
) -> int:
    cursor = conexion.cursor()
    cursor.executemany(
        "INSERT OR IGNORE INTO indicadores (codigo, nombre) VALUES (?, ?)",
        list(indicadores.items()),
    )
    conexion.commit()
    logger.info("Catálogo de indicadores poblado (%d indicadores).", len(indicadores))
    return len(indicadores)


def insertar_valores(
    conexion: sqlite3.Connection, registros: List[Tuple[str, str, int, Optional[float]]]
) -> int:
    cursor = conexion.cursor()
    cursor.executemany(
        "INSERT OR REPLACE INTO valores (pais, indicador_codigo, anio, valor) "
        "VALUES (?, ?, ?, ?)",
        registros,
    )
    conexion.commit()
    cantidad = len(registros)
    logger.info("%d observaciones insertadas en la base de datos.", cantidad)
    return cantidad


def _importar_wbgapi():
    try:
        import wbgapi as wb
        return wb
    except ImportError:
        raise ImportError(
            "La librería 'wbgapi' no está instalada. "
            "Ejecute: pip install wbgapi"
        )


def descargar_datos(
    codigos_indicadores: List[str],
    pais: str,
    anios: range,
) -> pd.DataFrame:
    wb = _importar_wbgapi()
    try:
        logger.info(
            "Descargando datos del Banco Mundial para %s (%d años)...",
            pais,
            len(anios),
        )
        df = wb.data.DataFrame(codigos_indicadores, [pais], time=anios)
        df = df.reset_index()
        if df.empty:
            raise RuntimeError(
                "La API del Banco Mundial retornó un DataFrame vacío."
            )
        if "economy" not in df.columns:
            df["economy"] = pais
        return df
    except Exception as e:
        raise RuntimeError(f"Error al descargar datos de la API: {e}")


def transformar_datos(df: pd.DataFrame) -> pd.DataFrame:
    columnas_requeridas = ["economy", "series"]
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(
                f"Columna esperada '{col}' no encontrada en el DataFrame. "
                "La API de wbgapi pudo haber cambiado su formato."
            )
    df_long = df.melt(
        id_vars=["economy", "series"], var_name="Year", value_name="Value"
    )
    if df_long.empty:
        raise ValueError("El DataFrame transformado está vacío.")
    try:
        df_long["Year"] = df_long["Year"].str.replace("YR", "").astype(int)
    except (ValueError, AttributeError) as e:
        raise ValueError(
            f"Error al convertir la columna Year: {e}. "
            "El formato de años de wbgapi pudo haber cambiado."
        )
    df_long = df_long.replace({np.nan: None})
    return df_long


def validar_datos(
    df_long: pd.DataFrame,
    indicadores: Dict[str, str],
    anio_minimo: int = 1990,
    anio_maximo: Optional[int] = None,
) -> pd.DataFrame:
    if anio_maximo is None:
        anio_maximo = pd.Timestamp.now().year
    fuera_rango_anios = df_long[
        (df_long["Year"] < anio_minimo) | (df_long["Year"] > anio_maximo)
    ]
    if not fuera_rango_anios.empty:
        logger.warning(
            "Se encontraron %d registros con años fuera del rango [%d, %d].",
            len(fuera_rango_anios),
            anio_minimo,
            anio_maximo,
        )
    for codigo, (min_val, max_val) in RANGOS_VALIDOS.items():
        mascara = df_long["series"] == codigo
        valores = df_long.loc[mascara, "Value"]
        if min_val is not None:
            fuera = valores < min_val
            cantidad_fuera = fuera.sum()
            if cantidad_fuera > 0:
                logger.warning(
                    "Indicador %s: %d valores por debajo del mínimo %.1f.",
                    codigo,
                    cantidad_fuera,
                    min_val,
                )
                df_long.loc[mascara & (df_long["Value"] < min_val), "Value"] = None
        if max_val is not None:
            fuera = valores > max_val
            cantidad_fuera = fuera.sum()
            if cantidad_fuera > 0:
                logger.warning(
                    "Indicador %s: %d valores por encima del máximo %.1f.",
                    codigo,
                    cantidad_fuera,
                    max_val,
                )
                df_long.loc[mascara & (df_long["Value"] > max_val), "Value"] = None
    nulls = df_long["Value"].isna().sum()
    if nulls > 0:
        logger.info("Total de valores nulos después de validación: %d.", nulls)
    return df_long


def preparar_registros(
    df_long: pd.DataFrame,
) -> List[Tuple[str, str, int, Optional[float]]]:
    registros: List[Tuple[str, str, int, Optional[float]]] = []
    for _, fila in df_long.iterrows():
        registros.append(
            (
                str(fila["economy"]),
                str(fila["series"]),
                int(fila["Year"]),
                fila["Value"],
            )
        )
    return registros


def main() -> None:
    logger.info("Iniciando inicialización y sincronización de base de datos...")
    conexion: Optional[sqlite3.Connection] = None
    try:
        conexion = conectar_base_datos(DB_NAME)
        ejecutar_esquema(conexion, SCHEMA_FILE)
        poblar_indicadores(conexion, INDICADORES)
        anio_actual = pd.Timestamp.now().year
        anios = range(anio_actual - ANIOS_HISTORIA, anio_actual + 1)
        df = descargar_datos(list(INDICADORES.keys()), PAIS, anios)
        df_long = transformar_datos(df)
        df_long = validar_datos(df_long, INDICADORES)
        registros = preparar_registros(df_long)
        insertar_valores(conexion, registros)
        logger.info("Sincronización finalizada exitosamente.")
    except FileNotFoundError as e:
        logger.error("Esquema no encontrado: %s", e)
        sys.exit(1)
    except (ValueError, RuntimeError) as e:
        logger.error("Error en el pipeline de datos: %s", e)
        if conexion:
            conexion.rollback()
        sys.exit(1)
    except sqlite3.Error as e:
        logger.error("Error en la base de datos: %s", e)
        if conexion:
            conexion.rollback()
        sys.exit(1)
    except ImportError as e:
        logger.error("Dependencia faltante: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.error("Error inesperado: %s", e)
        if conexion:
            conexion.rollback()
        sys.exit(1)
    finally:
        if conexion:
            conexion.close()
            logger.info("Conexión cerrada.")


if __name__ == "__main__":
    main()
