import xml.etree.ElementTree as ET
import zipfile
import pandas as pd

AUTH_NS = "urn:iso:std:iso:20022:tech:xsd:auth.036.001.02"

class Parser:
    """
    Handles XML parsing and extraction logic.
    """

    def get_second_dltins_link(self, xml_path: str) -> str:
        """
        Extract the second DLTINS download link from XML.
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()

        links = []

        for doc in root.findall(".//doc"):
            file_type = None
            download_link = None

            for child in doc:
                if child.attrib.get("name") == "file_type":
                    file_type = child.text
                if child.attrib.get("name") == "download_link":
                    download_link = child.text

            if file_type == "DLTINS":
                links.append(download_link)

        if len(links) < 2:
            raise ValueError("Less than 2 DLTINS links found")

        return links[1]

    def extract_zip(self, zip_path: str, extract_to: str) -> str:
        """
        Extract ZIP file and return extracted XML file path.
        """
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)

            for file in zip_ref.namelist():
                if file.endswith(".xml"):
                    return f"{extract_to}/{file}"

        raise FileNotFoundError("No XML file found in ZIP")

    def parse_xml(self, xml_path: str) -> pd.DataFrame:
        """
        Parse full XML into DataFrame.
        Structure: FinInstrm > ModfdRcrd > FinInstrmGnlAttrbts + Issr
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()

        data = []

        for instr in root.iter(f"{{{AUTH_NS}}}FinInstrm"):

            # The actual data is inside ModfdRcrd, not directly under FinInstrm
            record = instr.find(f"{{{AUTH_NS}}}ModfdRcrd")
            if record is None:
                continue

            gnl  = record.find(f"{{{AUTH_NS}}}FinInstrmGnlAttrbts")
            issr = record.find(f"{{{AUTH_NS}}}Issr")

            if gnl is None:
                continue

            row = {
                "FinInstrmGnlAttrbts.Id":             gnl.findtext(f"{{{AUTH_NS}}}Id"),
                "FinInstrmGnlAttrbts.FullNm":         gnl.findtext(f"{{{AUTH_NS}}}FullNm"),
                "FinInstrmGnlAttrbts.ClssfctnTp":     gnl.findtext(f"{{{AUTH_NS}}}ClssfctnTp"),
                "FinInstrmGnlAttrbts.CmmdtyDerivInd": gnl.findtext(f"{{{AUTH_NS}}}CmmdtyDerivInd"),
                "FinInstrmGnlAttrbts.NtnlCcy":        gnl.findtext(f"{{{AUTH_NS}}}NtnlCcy"),
                "Issr": issr.text if issr is not None else None,
            }

            data.append(row)

        return pd.DataFrame(data)