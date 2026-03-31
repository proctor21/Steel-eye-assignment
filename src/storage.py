import os
import fsspec
import pandas as pd
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class Storage:
    """
    Handles saving DataFrames locally or to cloud storage using fsspec.

    Supports:
        - Local filesystem
        - AWS S3     (s3://bucket/path/file.csv)
        - Azure Blob (az://container/path/file.csv)
    """

    def save_csv(self, df: pd.DataFrame, path: str, **storage_options) -> None:
        """
        Save DataFrame to CSV. Supports local, AWS S3, and Azure Blob via fsspec.

        Args:
            df (pd.DataFrame): DataFrame to save.
            path (str): Destination path. Examples:
                        - 'output/result.csv'              (local)
                        - 's3://bucket/data.csv'           (AWS S3)
                        - 'az://container/data.csv'        (Azure Blob)
            **storage_options: fsspec credentials.
                        For S3:    key, secret, token
                        For Azure: account_name, account_key
        """
        logger.info(f"Saving DataFrame to CSV at {path}")
        with fsspec.open(path, mode="w", newline="", **storage_options) as f:
            df.to_csv(f, index=False)
        logger.info("CSV saved successfully")

        if path.startswith(("s3://", "az://")):
            self.verify_cloud(path, storage_options)
        else:
            self.verify_local(path)

    def save_csv_cloud(self, df: pd.DataFrame, path: str, storage_options: Optional[Dict] = None) -> None:
        """
        Save DataFrame to cloud storage using fsspec.

        Args:
            df (pd.DataFrame): DataFrame to save.
            path (str): Cloud path (e.g., s3://bucket/file.csv or az://container/file.csv).
            storage_options (Dict, optional): fsspec storage options.
        """
        logger.info(f"Saving DataFrame to cloud path {path}")
        df.to_csv(path, index=False, storage_options=storage_options or {})
        logger.info("Cloud CSV saved successfully")
        self.verify_cloud(path, storage_options)

    def verify_local(self, path: str) -> None:
        """
        Verify a local CSV file exists and log its row count and size.

        Args:
            path (str): Local file path to verify.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Output file not found at: {path}")

        size_kb = os.path.getsize(path) / 1024
        df = pd.read_csv(path)
        logger.info(
            "Verification passed — rows: %d, columns: %d, size: %.1f KB",
            len(df), len(df.columns), size_kb,
        )

    def verify_cloud(self, path: str, storage_options: Optional[Dict] = None) -> None:
        """
        Verify a cloud CSV file exists using fsspec and log its row count.

        Args:
            path (str): Cloud path to verify (e.g., s3://bucket/file.csv).
            storage_options (Dict, optional): fsspec storage options.

        Raises:
            FileNotFoundError: If the file is not found at the cloud path.
        """
        try:
            with fsspec.open(path, mode="r", **(storage_options or {})) as f:
                df = pd.read_csv(f)
            logger.info(
                "Cloud verification passed — rows: %d, columns: %d",
                len(df), len(df.columns),
            )
        except Exception as e:
            raise FileNotFoundError(f"Cloud file not found at {path}: {e}")