import os

from dotenv import load_dotenv
from entsoe import EntsoePandasClient


def make_client():
    load_dotenv()
    token = os.environ.get("ENTSOE_API_TOKEN")
    if not token:
        raise RuntimeError("Set ENTSOE_API_TOKEN in your environment or .env file.")

    return EntsoePandasClient(api_key=token)

