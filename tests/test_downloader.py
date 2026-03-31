"""
Unit tests for the Downloader class.
"""

from unittest.mock import MagicMock, patch
import os
import pytest
from src.downloader import Downloader


@pytest.fixture
def downloader(tmp_path):
    return Downloader()


def _mock_response(content: bytes) -> MagicMock:
    response = MagicMock()
    response.content = content
    response.raise_for_status = MagicMock()
    return response


class TestDownloader:
    def test_download_saves_file(self, tmp_path):
        downloader = Downloader()
        fake_content = b"<root><doc/></root>"
        output_path = str(tmp_path / "index.xml")

        with patch("src.downloader.requests.get", return_value=_mock_response(fake_content)):
            downloader.download("https://example.com/index.xml", output_path)

        assert os.path.exists(output_path)
        assert open(output_path, "rb").read() == fake_content

    def test_download_raises_on_http_error(self, tmp_path):
        downloader = Downloader()
        response = MagicMock()
        response.raise_for_status.side_effect = Exception("HTTP 500")
        output_path = str(tmp_path / "index.xml")

        with patch("src.downloader.requests.get", return_value=response):
            with pytest.raises(Exception, match="HTTP 500"):
                downloader.download("https://example.com/index.xml", output_path)