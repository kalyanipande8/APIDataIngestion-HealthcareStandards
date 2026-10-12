"""A real local HTTP server exposing a paginated JSON API of healthcare
records -- standing in for a real third-party healthcare data API
(honestly disclosed), so src/api_client.py can demonstrate genuine HTTP
pagination mechanics rather than reading a static file directly."""
from __future__ import annotations

import json
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

N_TOTAL_RECORDS = 15_300
PAGE_SIZE = 500

DIAGNOSES = ["type 2 diabetes", "essential hypertension", "hyperlipidemia", "asthma", "copd"]
PROCEDURES = ["office visit established patient", "basic metabolic panel", "electrocardiogram"]
LAB_TESTS = ["glucose", "hemoglobin a1c", "creatinine", "sodium"]


def _generate_record(i: int, rng: random.Random) -> dict:
    return {
        "record_id": i,
        "diagnosis_description": rng.choice(DIAGNOSES),
        "procedure_description": rng.choice(PROCEDURES),
        "lab_test_description": rng.choice(LAB_TESTS),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 -- silence request logging
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/records":
            self.send_response(404)
            self.end_headers()
            return

        params = parse_qs(parsed.query)
        page = int(params.get("page", ["0"])[0])
        rng = random.Random(167 + page)

        start = page * PAGE_SIZE
        end = min(start + PAGE_SIZE, N_TOTAL_RECORDS)
        records = [_generate_record(i, rng) for i in range(start, end)]
        has_more = end < N_TOTAL_RECORDS

        body = json.dumps({"records": records, "has_more": has_more, "page": page}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_server(port: int = 0) -> tuple[HTTPServer, threading.Thread, int]:
    server = HTTPServer(("127.0.0.1", port), Handler)
    actual_port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, actual_port


if __name__ == "__main__":
    server, thread, port = start_server()
    print(f"Mock API running on http://127.0.0.1:{port}/records")
    import time
    time.sleep(2)
    server.shutdown()
