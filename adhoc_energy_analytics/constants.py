import tempfile
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"
TEMP_DIR = Path(tempfile.gettempdir())


def create_dirs():
    for dir in [DATA_DIR, OUTPUT_DIR]:
        dir.mkdir(exist_ok=True)
