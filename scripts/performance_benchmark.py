"""
Performance Audit Script for NORMVAULT Phase 2.
Measures latency, memory usage, and throughput for moderately sized specifications.
"""
import time
import os
import httpx

try:
    import psutil
    process = psutil.Process(os.getpid())
except ImportError:
    process = None

def generate_moderate_specification(num_clauses: int = 30) -> str:
    clauses = []
    for i in range(1, num_clauses + 1):
        clauses.append(
            f"Clause {i}.1: The motor {i} shall have a rated power of {i * 5} kW. "
            f"The operating temperature for unit {i} shall be -10 °C to 50 °C. "
            f"The housing enclosure for assembly {i} shall be IP55."
        )
    return "\n\n".join(clauses)

def main():
    print("=== NORMVAULT PHASE 2 PERFORMANCE AUDIT ===")
    spec_text = generate_moderate_specification(num_clauses=25) # ~75 requirements
    print(f"Generated test specification: {len(spec_text)} characters, {len(spec_text.splitlines())} lines.")

    start_mem = process.memory_info().rss / (1024 * 1024) if process else 0

    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=60.0) as client:
        start_time = time.perf_counter()
        
        # Ingest text specification
        res = client.post("/api/v1/specifications/text", json={
            "title": "Large Scale Power Plant Motor Schedule",
            "department": "Thermal Power Corporation",
            "raw_content": spec_text
        })
        duration = time.perf_counter() - start_time
        
        end_mem = process.memory_info().rss / (1024 * 1024) if process else 0

        print(f"\nResponse Status Code: {res.status_code}")
        data = res.json()
        req_count = data.get("requirements_count", 0)
        doc_id = data.get("document_id")
        print(f"Requirements Extracted: {req_count}")
        print(f"Total Request Duration: {duration:.4f} seconds ({duration * 1000:.2f} ms)")
        if req_count > 0:
            print(f"Throughput: {req_count / duration:.1f} requirements/sec")
        if process:
            print(f"Memory Delta: {end_mem - start_mem:.2f} MB (Current RSS: {end_mem:.2f} MB)")

        # Query requirements API latency
        if doc_id:
            req_start = time.perf_counter()
            req_res = client.get(f"/api/v1/documents/{doc_id}/requirements")
            req_duration = time.perf_counter() - req_start
            print(f"Requirements Retrieval Duration: {req_duration * 1000:.2f} ms (Retrieved {len(req_res.json()['requirements'])} items)")

if __name__ == "__main__":
    main()
