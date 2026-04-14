# ENTSO-E Data Toolkit

Download, process, and plot ENTSO-E data.

This first version includes actual generation by production type:

- download ENTSO-E actual generation
- convert interval MW observations to MWh
- aggregate monthly
- compute generation shares
- group small technologies into `Other` for plots
- save CSVs and PNGs

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Add your ENTSO-E token to `.env`:

```text
ENTSOE_API_TOKEN=your-token-here
```

## Run

```bash
python scripts/run_generation.py
```

Outputs are saved to:

```text
data/processed/generation/
outputs/plots/generation/
```

