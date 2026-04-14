import numpy as np
import pandas as pd

from entsoe_toolkit import config


def normalize_generation(raw):
    if isinstance(raw, pd.Series):
        data = raw.to_frame()
    else:
        data = raw.copy()

    data.index = pd.to_datetime(data.index)
    if data.index.tz is None:
        data.index = data.index.tz_localize(config.TIMEZONE)
    else:
        data.index = data.index.tz_convert(config.TIMEZONE)

    start = pd.Timestamp(config.START, tz=config.TIMEZONE)
    end_exclusive = pd.Timestamp(config.END_EXCLUSIVE, tz=config.TIMEZONE)
    data = data.loc[(data.index >= start) & (data.index < end_exclusive)]

    if isinstance(data.columns, pd.MultiIndex):
        metric = data.columns.get_level_values(-1).astype(str).str.lower()
        technology = data.columns.get_level_values(0)
        data = data.loc[:, metric == "actual aggregated"]
        data.columns = technology[metric == "actual aggregated"]

    numeric_cols = data.select_dtypes("number").columns
    generation_cols = [col for col in numeric_cols if "consumption" not in str(col).lower()]
    if not generation_cols:
        raise ValueError("No generation columns found in ENTSO-E response.")

    return data[generation_cols]


def infer_interval_hours(index):
    index = pd.DatetimeIndex(index).sort_values()
    if len(index) <= 1:
        return pd.Series(1.0, index=index)

    raw_gaps = (index[1:] - index[:-1]).total_seconds() / 3600
    normal_gap = float(pd.Series(raw_gaps).loc[lambda values: values > 0].median())
    if not np.isfinite(normal_gap) or normal_gap <= 0:
        normal_gap = 1.0

    gaps = pd.Series(raw_gaps, index=index[:-1])
    previous_gaps = pd.Series(raw_gaps, index=index[1:])
    hours = gaps.reindex(index).fillna(previous_gaps.reindex(index)).ffill().bfill()
    hours = hours.where((hours > 0) & np.isfinite(hours), normal_gap)
    return hours.clip(upper=normal_gap * 3)


def to_monthly_mwh(generation):
    interval_hours = infer_interval_hours(generation.index)
    energy_mwh = generation.mul(interval_hours, axis=0)
    monthly_mwh = energy_mwh.resample("MS").sum(min_count=1)
    monthly_mwh.index = monthly_mwh.index.tz_localize(None)
    return monthly_mwh.loc["2020-01":"2026-03"]


def monthly_generation_shares(monthly_mwh):
    total = monthly_mwh.sum(axis=1, min_count=1)
    shares = monthly_mwh.div(total, axis=0)
    shares[total <= 0] = np.nan
    return shares


def group_small_technologies(monthly_mwh, threshold=config.OTHER_THRESHOLD):
    total_by_technology = monthly_mwh.sum(axis=0, min_count=1)
    total_generation = total_by_technology.sum()
    if not np.isfinite(total_generation) or total_generation <= 0:
        return monthly_mwh

    small_columns = total_by_technology.index[(total_by_technology / total_generation) < threshold].tolist()
    if not small_columns:
        return monthly_mwh

    grouped = monthly_mwh.drop(columns=small_columns).copy()
    grouped["Other"] = monthly_mwh[small_columns].sum(axis=1, min_count=1)
    return grouped


def validate_monthly_shares(area_name, shares):
    row_sums = shares.sum(axis=1, min_count=1)
    bad_rows = row_sums.dropna().loc[lambda values: ~np.isclose(values, 1.0, atol=0.001)]
    if not bad_rows.empty:
        month = bad_rows.index[0].strftime("%Y-%m")
        raise ValueError(f"{area_name}: generation shares do not sum to 1 in {month}.")

