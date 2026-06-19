import streamlit as st

from application.transformer import DataTransformer
from domain.use_cases import GetIndicatorsUseCase
from infrastructure.api.worldbank import WorldBankSource
from infrastructure.persistence.sqlite import SQLiteRepository
from infrastructure.presentation.streamlit import render_dashboard


def main() -> None:
    api_source = WorldBankSource()
    db_repo = SQLiteRepository()
    transformer = DataTransformer()
    use_case = GetIndicatorsUseCase(api_source, db_repo, transformer)

    render_dashboard(st.cache_data(ttl=86400)(use_case.execute))


if __name__ == "__main__":
    main()
