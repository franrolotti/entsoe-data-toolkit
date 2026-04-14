import re

import pandas as pd

from entsoe_toolkit import config


def file_stem(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def monthly_mwh_path(area_name):
    return config.PROCESSED_GENERATION_DIR / f"{file_stem(area_name)}_monthly_generation_mwh.csv"


def monthly_shares_path(area_name):
    return config.PROCESSED_GENERATION_DIR / f"{file_stem(area_name)}_monthly_generation_shares.csv"


def plot_path(area_name):
    return config.GENERATION_PLOT_DIR / f"{file_stem(area_name)}_monthly_generation_shares.png"


def cached_monthly_mwh_is_complete(monthly_mwh):
    if monthly_mwh.empty:
        return False

    index = pd.to_datetime(monthly_mwh.index)
    return index.min() <= pd.Timestamp("2020-01-01") and index.max() >= pd.Timestamp("2026-03-01")


def load_cached_monthly_mwh(area_name):
    path = monthly_mwh_path(area_name)
    if not path.exists():
        return None

    monthly_mwh = pd.read_csv(path, index_col=0, parse_dates=True)
    if cached_monthly_mwh_is_complete(monthly_mwh):
        print(f"Using cached monthly MWh for {area_name}: {path}")
        return monthly_mwh.loc["2020-01":"2026-03"]

    print(f"Cache exists but is incomplete for {area_name}: {path}")
    return None

