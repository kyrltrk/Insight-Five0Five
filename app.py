import streamlit as st

from application.anomaly_detector import NumPyAnomalyDetector
from application.transformer import DataTransformer
from config.settings import DB_NAME, INDICATORS, PAIS
from domain.use_cases import GetIndicatorsUseCase
from infrastructure.api.worldbank import WorldBankSource
from infrastructure.persistence.sqlite import SQLiteRepository
from infrastructure.presentation.streamlit import render_dashboard

# ==============================================================================
# PUNTO DE COMPOSICIÓN / INYECCIÓN DE DEPENDENCIAS (DIP)
# ==============================================================================
# En el main del programa ensamblamos todas las piezas inyectando las
# dependencias concretas (SQLiteRepository, NumPyAnomalyDetector, DataTransformer)
# en sus respectivos puertos/abstracciones. También inyectamos configuraciones (OCP).
# ==============================================================================

def main() -> None:
    api_source = WorldBankSource()
    # SRP & LSP: SQLiteRepository se inicializa con la ruta del archivo de base de datos
    db_repo = SQLiteRepository(DB_NAME)
    transformer = DataTransformer()
    anomaly_detector = NumPyAnomalyDetector()
    
    # OCP: Inyectamos los indicadores y el país directamente en el caso de uso
    use_case = GetIndicatorsUseCase(
        api_source=api_source,
        db_repo=db_repo,
        transformer=transformer,
        indicators=INDICATORS,
        country=PAIS,
    )

    # SRP: Pasamos el calculador de anomalías a la vista
    render_dashboard(
        st.cache_data(ttl=86400)(use_case.execute),
        anomaly_detector
    )


if __name__ == "__main__":
    main()

