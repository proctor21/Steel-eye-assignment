import re
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class Transformer:
    """
    Handles data transformations on the parsed financial instruments DataFrame.

    Adds the following derived columns:
    - a_count: number of times the letter 'a' (case-insensitive) appears
      in FinInstrmGnlAttrbts.FullNm (0 when missing).
    - contains_a: 'YES' if a_count > 0, 'NO' otherwise.
    """

    def add_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a_count and contains_a columns to the DataFrame.

        Args:
            df: Parsed DataFrame containing FinInstrmGnlAttrbts.FullNm column.

        Returns:
            A new DataFrame with two additional columns: a_count and contains_a.

        Raises:
            ValueError: If the required column is not present in the DataFrame.
        """
        if "FinInstrmGnlAttrbts.FullNm" not in df.columns:
            raise ValueError("Column 'FinInstrmGnlAttrbts.FullNm' not found in DataFrame")

        df = df.copy()

        logger.info("Adding 'a_count' column...")
        df["a_count"] = (
            df["FinInstrmGnlAttrbts.FullNm"]
            .fillna("")
            .str.count("a", flags=re.IGNORECASE)
        )

        logger.info("Adding 'contains_a' column...")
        df["contains_a"] = df["a_count"].apply(lambda x: "YES" if x > 0 else "NO")

        logger.info("Transformation complete. Shape: %s", df.shape)
        return df