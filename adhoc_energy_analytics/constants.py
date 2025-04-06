import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CONFIG_DIR = PROJECT_ROOT / "config"
TEMP_DIR = Path(tempfile.gettempdir())


def get_default_download_dir():
    return RAW_DATA_DIR


if __name__ == "__main__":
    # Print all paths for debugging
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"RAW_DATA_DIR: {RAW_DATA_DIR}")
    print(f"PROCESSED_DATA_DIR: {PROCESSED_DATA_DIR}")
    print(f"CONFIG_DIR: {CONFIG_DIR}")
    print(f"TEMP_DIR: {TEMP_DIR}")
