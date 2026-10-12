"""End-to-end: start the mock API, ingest all records via real HTTP
pagination, map to 4 healthcare standards, and check interoperability."""
import json
import os

from src.mock_api_server import start_server
from src.api_client import fetch_all_records
from src.standards_mapping import map_all_standards
from src.interoperability_check import check_interoperability

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Starting local mock healthcare data API ===")
server, thread, port = start_server()
print(f"API running on http://127.0.0.1:{port}/records")

try:
    print("\n=== Ingesting records via real HTTP pagination ===")
    df = fetch_all_records(f"http://127.0.0.1:{port}")
    df.to_csv("data/ingested_records.csv", index=False)
    print(f"{len(df)} records ingested across {df['record_id'].max() // 500 + 1} pages")

    print("\n=== Mapping to ICD-10-CM, CPT, LOINC, FHIR ===")
    mapped = map_all_standards(df)
    mapped.to_csv("data/mapped_records.csv", index=False)

    print("\n=== Interoperability check (all 4 standards) ===")
    interop = check_interoperability(mapped)
    print(interop)

    summary = {
        "n_records_ingested": len(df),
        "n_fully_interoperable": interop["n_fully_interoperable"],
        "interoperability_pct": interop["interoperability_pct"],
    }
    with open("results/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))
finally:
    server.shutdown()
