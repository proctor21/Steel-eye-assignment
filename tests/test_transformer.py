"""
Unit tests for the Transformer class.
"""

import pandas as pd
import pytest
from src.transformer import Transformer


@pytest.fixture
def transformer():
    return Transformer()


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "FinInstrmGnlAttrbts.Id": ["ID1", "ID2", "ID3", "ID4"],
        "FinInstrmGnlAttrbts.FullNm": ["Alpha Fund", "BETA CORP", "no vowel", None],
        "FinInstrmGnlAttrbts.ClssfctnTp": ["RSSTXX", "RFSTCB", "RWSNCA", "RSSTXX"],
        "FinInstrmGnlAttrbts.CmmdtyDerivInd": ["false", "true", "false", "false"],
        "FinInstrmGnlAttrbts.NtnlCcy": ["EUR", "USD", "GBP", "EUR"],
        "Issr": ["ISS1", "ISS2", "ISS3", "ISS4"],
    })


class TestAddColumns:
    def test_adds_both_columns(self, transformer, sample_df):
        result = transformer.add_columns(sample_df)
        assert "a_count" in result.columns
        assert "contains_a" in result.columns

    def test_a_count_case_insensitive(self, transformer, sample_df):
        result = transformer.add_columns(sample_df)
        assert result.iloc[0]["a_count"] == 2  # Alpha Fund -> a, A
        assert result.iloc[1]["a_count"] == 1  # BETA CORP  -> A
        assert result.iloc[2]["a_count"] == 0  # no vowel   -> 0

    def test_null_counts_as_zero(self, transformer, sample_df):
        result = transformer.add_columns(sample_df)
        assert result.iloc[3]["a_count"] == 0
        assert result.iloc[3]["contains_a"] == "NO"

    def test_contains_a_yes(self, transformer, sample_df):
        result = transformer.add_columns(sample_df)
        assert result.iloc[0]["contains_a"] == "YES"

    def test_contains_a_no(self, transformer, sample_df):
        result = transformer.add_columns(sample_df)
        assert result.iloc[2]["contains_a"] == "NO"

    def test_does_not_mutate_input(self, transformer, sample_df):
        original_cols = list(sample_df.columns)
        transformer.add_columns(sample_df)
        assert list(sample_df.columns) == original_cols

    def test_raises_when_column_missing(self, transformer):
        df = pd.DataFrame({"other": ["value"]})
        with pytest.raises(ValueError):
            transformer.add_columns(df)