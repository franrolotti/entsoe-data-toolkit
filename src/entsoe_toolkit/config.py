from pathlib import Path

START = "2020-01-01"
END_EXCLUSIVE = "2026-04-01"
TIMEZONE = "Europe/Paris"
CHUNK_DAYS = 183
OTHER_THRESHOLD = 0.02
FORCE_DOWNLOAD = False

AREAS = {
    "Spain": "ES",
    "France": "FR",
    "Portugal": "PT",
    "Italy": "IT",
    "Germany": "DE_LU",
    "Belgium": "BE",
    "Netherlands": "NL",
}

DATA_DIR = Path("data")
PROCESSED_GENERATION_DIR = DATA_DIR / "processed" / "generation"
GENERATION_PLOT_DIR = Path("outputs") / "plots" / "generation"

