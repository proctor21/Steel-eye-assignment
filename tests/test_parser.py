"""
Unit tests for the Parser class.
"""

import os
import zipfile
import pytest
from src.parser import Parser

AUTH_NS = "urn:iso:std:iso:20022:tech:xsd:auth.036.001.02"


def _write_index_xml(path: str, links: list) -> None:
    docs = ""
    for file_type, url in links:
        docs += f"""
        <doc>
            <str name="file_type">{file_type}</str>
            <str name="download_link">{url}</str>
        </doc>"""
    with open(path, "w") as f:
        f.write(f"<response><r>{docs}</r></response>")


def _write_dltins_xml(path: str, records: list) -> None:
    items = ""
    for r in records:
        items += f"""
        <ns0:FinInstrm xmlns:ns0="{AUTH_NS}">
          <ns0:ModfdRcrd>
            <ns0:FinInstrmGnlAttrbts>
              <ns0:Id>{r.get("Id", "")}</ns0:Id>
              <ns0:FullNm>{r.get("FullNm", "")}</ns0:FullNm>
              <ns0:ClssfctnTp>{r.get("ClssfctnTp", "")}</ns0:ClssfctnTp>
              <ns0:CmmdtyDerivInd>{r.get("CmmdtyDerivInd", "")}</ns0:CmmdtyDerivInd>
              <ns0:NtnlCcy>{r.get("NtnlCcy", "")}</ns0:NtnlCcy>
            </ns0:FinInstrmGnlAttrbts>
            <ns0:Issr>{r.get("Issr", "")}</ns0:Issr>
          </ns0:ModfdRcrd>
        </ns0:FinInstrm>"""
    with open(path, "w") as f:
        f.write(f'<root xmlns:ns0="{AUTH_NS}">{items}</root>')


@pytest.fixture
def parser():
    return Parser()


class TestGetSecondDltinsLink:
    def test_returns_second_link(self, parser, tmp_path):
        path = str(tmp_path / "index.xml")
        _write_index_xml(path, [
            ("DLTINS", "https://example.com/first.zip"),
            ("DLTINS", "https://example.com/second.zip"),
        ])
        assert parser.get_second_dltins_link(path) == "https://example.com/second.zip"

    def test_raises_when_less_than_two(self, parser, tmp_path):
        path = str(tmp_path / "index.xml")
        _write_index_xml(path, [("DLTINS", "https://example.com/first.zip")])
        with pytest.raises(ValueError):
            parser.get_second_dltins_link(path)

    def test_ignores_non_dltins(self, parser, tmp_path):
        path = str(tmp_path / "index.xml")
        _write_index_xml(path, [
            ("OTHER", "https://example.com/other.zip"),
            ("DLTINS", "https://example.com/first.zip"),
            ("DLTINS", "https://example.com/second.zip"),
        ])
        assert parser.get_second_dltins_link(path) == "https://example.com/second.zip"


class TestExtractZip:
    def test_extracts_xml(self, parser, tmp_path):
        zip_path = str(tmp_path / "test.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("data.xml", "<root/>")
        result = parser.extract_zip(zip_path, str(tmp_path / "out"))
        assert result.endswith("data.xml")
        assert os.path.exists(result)

    def test_raises_when_no_xml(self, parser, tmp_path):
        zip_path = str(tmp_path / "test.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("readme.txt", "no xml")
        with pytest.raises(FileNotFoundError):
            parser.extract_zip(zip_path, str(tmp_path / "out"))


class TestParseXml:
    def test_parses_records(self, parser, tmp_path):
        path = str(tmp_path / "dltins.xml")
        _write_dltins_xml(path, [
            {"Id": "ID1", "FullNm": "Alpha Fund", "ClssfctnTp": "RSSTXX",
             "CmmdtyDerivInd": "false", "NtnlCcy": "EUR", "Issr": "ISS1"},
        ])
        df = parser.parse_xml(path)
        assert len(df) == 1
        assert df.iloc[0]["FinInstrmGnlAttrbts.Id"] == "ID1"

    def test_empty_xml_returns_empty_df(self, parser, tmp_path):
        path = str(tmp_path / "empty.xml")
        with open(path, "w") as f:
            f.write("<root/>")
        df = parser.parse_xml(path)
        assert len(df) == 0