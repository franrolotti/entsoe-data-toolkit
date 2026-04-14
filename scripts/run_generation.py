from entsoe_toolkit import config, io
from entsoe_toolkit.client import make_client
from entsoe_toolkit.download import query_generation_in_chunks
from entsoe_toolkit.plot import plot_generation_shares
from entsoe_toolkit.process import (
    group_small_technologies,
    monthly_generation_shares,
    normalize_generation,
    to_monthly_mwh,
    validate_monthly_shares,
)


def main():
    config.PROCESSED_GENERATION_DIR.mkdir(parents=True, exist_ok=True)
    config.GENERATION_PLOT_DIR.mkdir(parents=True, exist_ok=True)

    client = None

    for area_name, country_code in config.AREAS.items():
        monthly_mwh = None if config.FORCE_DOWNLOAD else io.load_cached_monthly_mwh(area_name)

        if monthly_mwh is None:
            if client is None:
                client = make_client()

            print(f"\nDownloading {area_name} ({country_code})")
            raw = query_generation_in_chunks(client, country_code)
            generation = normalize_generation(raw)
            monthly_mwh = to_monthly_mwh(generation)

        shares = monthly_generation_shares(monthly_mwh)
        validate_monthly_shares(area_name, shares)

        plot_mwh = group_small_technologies(monthly_mwh)
        plot_shares = monthly_generation_shares(plot_mwh)
        validate_monthly_shares(area_name, plot_shares)

        monthly_mwh.to_csv(io.monthly_mwh_path(area_name))
        shares.to_csv(io.monthly_shares_path(area_name))
        plot_path = plot_generation_shares(area_name, plot_shares)
        print(f"Saved {plot_path}")


if __name__ == "__main__":
    main()

