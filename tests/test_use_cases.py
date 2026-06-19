import numpy as np
import pandas as pd
import pytest

from application.transformer import DataTransformer
from application.validator import DataValidator
from domain.exceptions import ApiCaidaError, DatosNoEncontradosError
from domain.use_cases import GetIndicatorsUseCase, PopulateDatabaseUseCase
from tests.fakes import FakeRepository, FakeSource


@pytest.fixture
def transformer():
    return DataTransformer()


@pytest.fixture
def validator():
    return DataValidator()


def _make_fake_api_data(country="NIC"):
    data = {
        "economy": [country, country],
        "series": ["IT.NET.USER.ZS", "EG.ELC.ACCS.ZS"],
    }
    for y in range(2010, 2026):
        data[f"YR{y}"] = [30.0 + (y - 2010) * 0.5, 70.0 + (y - 2010) * 0.3]
    return pd.DataFrame(data)


def _make_fake_db_data():
    rows = []
    for year in range(2010, 2026):
        rows.append(
            {
                "economy": "NIC",
                "series": "IT.NET.USER.ZS",
                "Year": year,
                "Value": 30.0 + (year - 2010) * 0.5,
                "Indicator": "Uso de Internet (%)",
            }
        )
        rows.append(
            {
                "economy": "NIC",
                "series": "EG.ELC.ACCS.ZS",
                "Year": year,
                "Value": 70.0 + (year - 2010) * 0.3,
                "Indicator": "Acceso a Electricidad (%)",
            }
        )
    return pd.DataFrame(rows)


class TestGetIndicatorsUseCase:
    def test_fetches_from_api_when_available(self, transformer):
        source = FakeSource(data=_make_fake_api_data())
        repo = FakeRepository()
        use_case = GetIndicatorsUseCase(source, repo, transformer)

        df_long, df_wide = use_case.execute()

        assert not df_long.empty
        assert not df_wide.empty
        assert "Year" in df_wide.columns
        assert source.call_count == 1

    def test_falls_back_to_db_when_api_fails(self, transformer):
        source = FakeSource(should_fail=True)
        repo = FakeRepository(data=_make_fake_db_data())
        use_case = GetIndicatorsUseCase(source, repo, transformer)

        df_long, df_wide = use_case.execute()

        assert not df_long.empty
        assert not df_wide.empty
        assert source.call_count == 1

    def test_raises_error_when_both_sources_fail(self, transformer):
        source = FakeSource(should_fail=True)
        repo = FakeRepository()
        use_case = GetIndicatorsUseCase(source, repo, transformer)

        with pytest.raises(DatosNoEncontradosError):
            use_case.execute()


class TestPopulateDatabaseUseCase:
    def test_executes_full_etl_pipeline(self, transformer, validator):
        source = FakeSource(data=_make_fake_api_data())
        repo = FakeRepository()
        use_case = PopulateDatabaseUseCase(source, repo, transformer, validator)

        use_case.execute()

        assert repo._was_connected
        assert repo._schema_executed
        assert len(repo._saved_indicators) > 0
        assert len(repo._saved_values) > 0

    def test_rolls_back_on_failure(self, transformer, validator):
        source = FakeSource(should_fail=True)
        repo = FakeRepository()
        use_case = PopulateDatabaseUseCase(source, repo, transformer, validator)

        with pytest.raises(ApiCaidaError):
            use_case.execute()


class TestDataTransformer:
    def test_process_api_data_returns_long_and_wide(self, transformer):
        raw = _make_fake_api_data()
        indicator_map = {
            "IT.NET.USER.ZS": "Uso de Internet (%)",
            "EG.ELC.ACCS.ZS": "Acceso a Electricidad (%)",
        }

        df_long, df_wide = transformer.process_api_data(raw, indicator_map)

        assert "Indicator" in df_long.columns
        assert "Uso de Internet (%)" in df_wide.columns
        assert len(df_wide) > 0

    def test_process_db_data_interpolates_and_pivots(self, transformer):
        raw = _make_fake_db_data()

        df_long, df_wide = transformer.process_db_data(raw)

        assert "Indicator" in df_long.columns
        assert len(df_wide) > 0

    def test_transform_populate_melts_and_cleans(self, transformer):
        raw = _make_fake_api_data()

        result = transformer.transform_populate(raw)

        assert "economy" in result.columns
        assert "series" in result.columns
        assert "Year" in result.columns
        assert "Value" in result.columns
        assert result["Year"].dtype == np.int32 or result["Year"].dtype == np.int64

    def test_to_records_converts_to_tuples(self, transformer):
        raw = _make_fake_api_data()
        df = transformer.transform_populate(raw)

        records = transformer.to_records(df)

        assert len(records) > 0
        assert isinstance(records[0], tuple)
        assert len(records[0]) == 4


class TestDataValidator:
    def test_validates_ranges_correctly(self, validator):
        data = {
            "economy": ["NIC", "NIC"],
            "series": ["IT.NET.USER.ZS", "IT.NET.USER.ZS"],
            "Year": [2020, 2021],
            "Value": [50.0, 150.0],
        }
        df = pd.DataFrame(data)
        rangos = {"IT.NET.USER.ZS": (0, 100)}

        result = validator.validate(df, rangos)

        assert result.loc[0, "Value"] == 50.0
        assert pd.isna(result.loc[1, "Value"])
