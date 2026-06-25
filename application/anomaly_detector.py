import numpy as np
from typing import List, Tuple
from domain.ports import AnomalyDetectorPort

# ==============================================================================
# PRINCIPIO DE RESPONSABILIDAD ÚNICA (SRP) y DEPENDENCY INVERSION (DIP)
# ==============================================================================
# Esta clase aísla el cálculo matemático de anomalías (desviaciones estándar)
# fuera de la capa de interfaz de usuario (Streamlit). Implementa AnomalyDetectorPort.
# ==============================================================================

class NumPyAnomalyDetector(AnomalyDetectorPort):
    def detect_anomalies(
        self, years: List[int], values: List[float], std_devs: float = 2.0
    ) -> List[Tuple[int, float]]:
        anomalies: List[Tuple[int, float]] = []
        
        # Filtrar valores nulos
        valid_indices = [i for i, val in enumerate(values) if val is not None]
        filtered_values = [values[i] for i in valid_indices]
        filtered_years = [years[i] for i in valid_indices]

        if len(filtered_values) <= 1:
            return anomalies

        # Calcular diferencias año a año
        diffs = np.diff(filtered_values)
        mean_diff = np.nanmean(diffs)
        std_diff = np.nanstd(diffs)

        if std_diff > 0:
            # Encontrar índices donde la diferencia difiere del promedio en más de std_devs desviaciones estándar
            outliers = np.where(
                np.abs(diffs - mean_diff) > std_devs * std_diff
            )[0]
            for idx in outliers:
                # La anomalía corresponde a la transición al año en idx + 1
                anomalies.append((int(filtered_years[idx + 1]), float(diffs[idx])))
                
        return anomalies
