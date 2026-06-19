from typing import List

import pandas as pd

from domain.exceptions import ApiCaidaError
from domain.ports import IndicatorSource


class WorldBankSource(IndicatorSource):
    def fetch_data(
        self, indicators: List[str], country: str, years: range
    ) -> pd.DataFrame:
        try:
            import wbgapi as wb

            df = wb.data.DataFrame(indicators, [country], time=years)
            df = df.reset_index()

            if df.empty:
                raise RuntimeError(
                    "La API del Banco Mundial retorno un DataFrame vacio."
                )

            if "economy" not in df.columns:
                df["economy"] = country

            return df
        except ImportError:
            raise ApiCaidaError(
                "La libreria 'wbgapi' no esta instalada. "
                "Ejecute: pip install wbgapi"
            )
        except Exception as e:
            raise ApiCaidaError(
                f"Error al descargar datos de la API del Banco Mundial: {e}"
            )
