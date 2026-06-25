from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# ==============================================================================
# PRINCIPIO DE INVERSIÓN DE DEPENDENCIAS (DIP)
# ==============================================================================
# DataTransformer ahora implementa de forma explícita el puerto DataTransformerPort
# definido en el Dominio, de modo que el dominio interactúa solo con la abstracción.
# ==============================================================================
from domain.ports import DataTransformerPort


class DataTransformer(DataTransformerPort):
    def process_api_data(
        self, raw_df: pd.DataFrame, indicator_map: Dict[str, str]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df_long = raw_df.melt(
            id_vars=["economy", "series"], var_name="Year", value_name="Value"
        )
        df_long["Year"] = df_long["Year"].str.replace("YR", "").astype(int)

        df_long["Value"] = df_long.groupby(["series"])["Value"].transform(
            lambda x: x.interpolate(method="linear", limit_direction="both")
        )

        df_long["Indicator"] = df_long["series"].map(indicator_map)

        df_wide = (
            df_long.pivot_table(
                index=["Year"], columns="Indicator", values="Value"
            )
            .reset_index()
        )

        return df_long, df_wide

    def process_db_data(
        self, df_long: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df_long["Value"] = df_long.groupby(["series"])["Value"].transform(
            lambda x: x.interpolate(method="linear", limit_direction="both")
        )

        df_wide = (
            df_long.pivot_table(
                index=["Year"], columns="Indicator", values="Value"
            )
            .reset_index()
        )

        return df_long, df_wide

    def transform_populate(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        columnas_requeridas = ["economy", "series"]
        for col in columnas_requeridas:
            if col not in raw_df.columns:
                raise ValueError(
                    f"Columna esperada '{col}' no encontrada en el DataFrame. "
                    "La API de wbgapi pudo haber cambiado su formato."
                )

        df_long = raw_df.melt(
            id_vars=["economy", "series"], var_name="Year", value_name="Value"
        )

        if df_long.empty:
            raise ValueError("El DataFrame transformado esta vacio.")

        try:
            df_long["Year"] = (
                df_long["Year"].str.replace("YR", "").astype(int)
            )
        except (ValueError, AttributeError) as e:
            raise ValueError(
                f"Error al convertir la columna Year: {e}. "
                "El formato de años de wbgapi pudo haber cambiado."
            )

        df_long = df_long.replace({np.nan: None})
        return df_long

    def to_records(
        self, df_long: pd.DataFrame
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
