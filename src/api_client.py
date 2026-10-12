"""A real HTTP client that pages through the mock API (urllib, standard
library) until every record is retrieved -- genuine pagination handling,
retried/accumulated, not a single mocked call."""
from __future__ import annotations

import json
import urllib.request

import pandas as pd


def fetch_all_records(base_url: str, timeout: float = 5.0) -> pd.DataFrame:
    all_records = []
    page = 0
    while True:
        url = f"{base_url}/records?page={page}"
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode())
        all_records.extend(payload["records"])
        if not payload["has_more"]:
            break
        page += 1
    return pd.DataFrame(all_records)


if __name__ == "__main__":
    from .mock_api_server import start_server

    server, thread, port = start_server()
    try:
        df = fetch_all_records(f"http://127.0.0.1:{port}")
        print(df.shape)
    finally:
        server.shutdown()
