import requests
import logging

logger = logging.getLogger(__name__)


class Downloader:
    def download(self, url: str, output_path: str) -> None:
        try:
            logger.info(f"Downloading from {url}")

            response = requests.get(
                url,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Saved to {output_path}")

        except Exception as e:
            logger.error(f"Error: {e}")
            raise