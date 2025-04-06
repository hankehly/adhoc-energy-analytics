import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from adhoc_energy_analytics.constants import get_default_download_dir


class EIAWholesaleElectricityMarketDataDownloader:
    """
    A class to download annual CSV wholesale electricity market data from the EIA website.
    The class fetches the webpage, extracts links to CSV files (ending with a 4-digit year),
    and downloads them to a specified directory while caching the etags.

    Example usage:
        downloader = EIAWholesaleElectricityMarketDataDownloader()
        downloader.download_files(overwrite=False, verbose=False)
    """

    def __init__(
        self,
        url="https://www.eia.gov/electricity/wholesalemarkets/data.php",
        download_dir=None,
    ):
        self.url = url
        self.pattern = re.compile(r".*\d{4}\.csv$")  # Targets annual CSV files
        directory = (
            download_dir if download_dir is not None else get_default_download_dir()
        )
        self.download_dir = Path(directory)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def fetch_page(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None

    def extract_links(self, soup):
        links = soup.find_all("a")
        return [
            link.get("href")
            for link in links
            if link.get("href") and self.pattern.match(link.get("href"))
        ]

    def download_files(self, overwrite=False, verbose=False):
        soup = self.fetch_page()
        if not soup:
            return

        all_links = self.extract_links(soup)
        for link in tqdm(all_links, desc="Downloading files"):
            file_url = urljoin(self.url, link)
            file_name = Path(link).name
            file_path = self.download_dir / file_name
            etag_path = self.download_dir / f"{file_name}.etag"

            existing_etag = None
            if etag_path.exists():
                existing_etag = etag_path.read_text().strip()

            new_etag = None
            # If not overwriting, perform HEAD request to check if file was modified.
            if not overwrite:
                head_response = requests.head(file_url)
                new_etag = head_response.headers.get("ETag")
                if existing_etag and new_etag and existing_etag == new_etag:
                    if verbose:
                        tqdm.write(f"{file_name} is already downloaded, skipping.")
                    continue

            # Download the file regardless if overwrite is True or file is modified.
            file_response = requests.get(file_url)
            if file_response.status_code == 200:
                file_path.write_bytes(file_response.content)
                new_etag = file_response.headers.get("ETag")
                if verbose:
                    tqdm.write(
                        f"Downloaded {file_name}"
                        + (" (overwritten)" if overwrite else "")
                    )
                if new_etag:
                    etag_path.write_text(new_etag)
            else:
                tqdm.write(f"Failed to download {file_url}")
