import time

import pandas as pd

from entsoe_toolkit import config


def query_generation_in_chunks(client, country_code):
    start = pd.Timestamp(config.START, tz=config.TIMEZONE)
    end_exclusive = pd.Timestamp(config.END_EXCLUSIVE, tz=config.TIMEZONE)
    parts = []

    while start < end_exclusive:
        end = min(start + pd.Timedelta(days=config.CHUNK_DAYS), end_exclusive)
        last_error = None

        for attempt in range(1, 4):
            try:
                data = client.query_generation(country_code=country_code, start=start, end=end)
                parts.append(data)
                print(f"{country_code}: {start.date()} to {(end - pd.Timedelta(days=1)).date()} downloaded")
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                print(f"{country_code}: retry {attempt} failed for {start.date()} to {end.date()}: {exc}")
                time.sleep(2 * attempt)

        if last_error is not None:
            raise last_error

        start = end

    data = pd.concat(parts).sort_index()
    return data.loc[~data.index.duplicated(keep="last")]

