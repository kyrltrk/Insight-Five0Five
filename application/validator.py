import logging
from typing import Dict, Optional, Tuple

import pandas as pd

logger = logging.getLogger("populate_db")


class DataValidator:
    def validate(
        self,
        df_long: pd.DataFrame,
        rangos: Dict[str, Tuple[Optional[float], Optional[float]]],
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

        for codigo, (min_val, max_val) in rangos.items():
            mascara = df_long["series"] == codigo

            if min_val is not None:
                fuera = df_long.loc[mascara, "Value"] < min_val
                cantidad_fuera = fuera.sum()
                if cantidad_fuera > 0:
                    logger.warning(
                        "Indicador %s: %d valores por debajo del minimo %.1f.",
                        codigo,
                        cantidad_fuera,
                        min_val,
                    )
                    df_long.loc[
                        mascara & (df_long["Value"] < min_val), "Value"
                    ] = None

            if max_val is not None:
                fuera = df_long.loc[mascara, "Value"] > max_val
                cantidad_fuera = fuera.sum()
                if cantidad_fuera > 0:
                    logger.warning(
                        "Indicador %s: %d valores por encima del maximo %.1f.",
                        codigo,
                        cantidad_fuera,
                        max_val,
                    )
                    df_long.loc[
                        mascara & (df_long["Value"] > max_val), "Value"
                    ] = None

        nulls = df_long["Value"].isna().sum()
        if nulls > 0:
            logger.info("Total de valores nulos despues de validacion: %d.", nulls)

        return df_long
