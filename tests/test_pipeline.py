import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.mock_api_server import start_server, N_TOTAL_RECORDS
from src.api_client import fetch_all_records
from src.standards_mapping import map_all_standards, ICD10_MAP, CPT_MAP, LOINC_MAP
from src.interoperability_check import check_interoperability


@pytest.fixture(scope="module")
def ingested():
    server, thread, port = start_server()
    try:
        df = fetch_all_records(f"http://127.0.0.1:{port}")
    finally:
        server.shutdown()
    return df


def test_pagination_retrieves_all_records(ingested):
    assert len(ingested) == N_TOTAL_RECORDS


def test_ingested_records_exceed_15000(ingested):
    assert len(ingested) >= 15000


def test_record_ids_are_unique_and_complete(ingested):
    assert ingested["record_id"].is_unique
    assert set(ingested["record_id"]) == set(range(N_TOTAL_RECORDS))


def test_standards_mapping_produces_real_codes(ingested):
    mapped = map_all_standards(ingested)
    assert set(mapped["icd10_code"].dropna().unique()) <= set(ICD10_MAP.values())
    assert set(mapped["cpt_code"].dropna().unique()) <= set(CPT_MAP.values())
    assert set(mapped["loinc_code"].dropna().unique()) <= set(LOINC_MAP.values())


def test_interoperability_is_complete(ingested):
    mapped = map_all_standards(ingested)
    result = check_interoperability(mapped)
    assert result["interoperability_pct"] == 100.0
