"""
Unit tests for the Storage class.
"""

import pandas as pd
import pytest
from src.storage import Storage


@pytest.fixture
def storage():
    return Storage()


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "FinInstrmGnlAttrbts.Id": ["ID1", "ID2"],
        "FinInstrmGnlAttrbts.FullNm": ["Alpha Fund", "Beta Corp"],
        "a_count": [2, 1],
        "contains_a": ["YES", "YES"],
    })


class TestSaveCsv:
    def test_saves_locally(self, storage, sample_df, tmp_path):
        path = str(tmp_path / "output.csv")
        storage.save_csv(sample_df, path)
        result = pd.read_csv(path)
        assert len(result) == 2

    def test_correct_columns(self, storage, sample_df, tmp_path):
        path = str(tmp_path / "output.csv")
        storage.save_csv(sample_df, path)
        result = pd.read_csv(path)
        assert list(result.columns) == list(sample_df.columns)

    def test_no_index_written(self, storage, sample_df, tmp_path):
        path = str(tmp_path / "output.csv")
        storage.save_csv(sample_df, path)
        with open(path) as f:
            header = f.readline()
        assert "Unnamed" not in header