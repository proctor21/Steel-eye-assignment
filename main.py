"""
Entry point for the SteelEye ESMA FIRDS data pipeline.

Pipeline steps:
    1. Download ESMA FIRDS index XML
    2. Extract the second DLTINS download link
    3. Download the DLTINS ZIP file
    4. Extract XML from the ZIP
    5. Parse XML into a DataFrame
    6. Add derived columns (a_count, contains_a)
    7. Save output CSV to local / S3 / Azure

Usage::

    python main.py
    python main.py --output s3://my-bucket/output/data.csv
    python main.py --output az://my-container/output/data.csv
"""

import argparse
import logging
import os

from src.downloader import Downloader
from src.parser import Parser
from src.transformer import Transformer
from src.storage import Storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

ESMA_URL = (
    "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select"
    "?q=*&fq=publication_date:%5B2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z%5D"
    "&wt=xml&indent=true&start=0&rows=100"
)


def run_pipeline(output_path: str = "output/result.csv", **storage_options) -> None:
    """
    Execute the full ESMA FIRDS data pipeline end to end.

    Args:
        output_path: fsspec-compatible destination path for the output CSV.
                     Defaults to 'output/result.csv' (local).
        **storage_options: Credentials forwarded to fsspec for cloud storage.
    """
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    downloader = Downloader()
    parser = Parser()
    transformer = Transformer()
    storage = Storage()

    # Step 1: Download index XML
    index_xml_path = "data/index.xml"
    downloader.download(ESMA_URL, index_xml_path)

    # Step 2: Extract second DLTINS link
    dltins_url = parser.get_second_dltins_link(index_xml_path)
    logger.info("Second DLTINS URL: %s", dltins_url)

    # Step 3: Download the ZIP
    zip_path = "data/dltins.zip"
    downloader.download(dltins_url, zip_path)

    # Step 4: Extract XML from ZIP
    xml_path = parser.extract_zip(zip_path, extract_to="data/extracted")

    # Step 5: Parse XML into DataFrame
    df = parser.parse_xml(xml_path)
    logger.info("Parsed %d rows.", len(df))

    # Step 6: Add derived columns
    df = transformer.add_columns(df)
    logger.info("Columns after transform: %s", list(df.columns))

    # Step 7: Save to storage
    storage.save_csv(df, output_path, **storage_options)
    logger.info("Pipeline complete. Output: %s", output_path)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="SteelEye ESMA FIRDS pipeline")
    arg_parser.add_argument(
        "--output",
        default="output/result.csv",
        help="Output path (local, s3://, or az://). Default: output/result.csv",
    )
    args = arg_parser.parse_args()
    run_pipeline(output_path=args.output)