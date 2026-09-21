"""
Live API Verification Script for NORMVAULT Phase 2 Endpoints.
Executes live HTTP requests to verify real JSON payloads for:
1. POST /api/v1/documents
2. POST /api/v1/documents/{id}/process
3. GET /api/v1/documents/{id}
4. GET /api/v1/documents/{id}/status
5. GET /api/v1/documents/{id}/content
6. GET /api/v1/documents/{id}/requirements
7. POST /api/v1/specifications/text
"""
import time
import json
import httpx

BASE_URL = "http://127.0.0.1:8000"

def main():
    print("=== NORMVAULT PHASE 2 LIVE API VERIFICATION ===")
    
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        # Check health
        h_res = client.get("/api/v1/health")
        print(f"[0] Health Check: Status {h_res.status_code} -> {h_res.json()['status']}")
        
        # 1. POST /api/v1/documents
        print("\n--- 1. POST /api/v1/documents ---")
        test_content = b"The motor shall have a rated power of 5 kW. The enclosure shall be IP55."
        upload_res = client.post(
            "/api/v1/documents",
            files={"file": ("live_test_tender.txt", test_content, "text/plain")}
        )
        print(f"Status: {upload_res.status_code}")
        upload_data = upload_res.json()
        print(f"Response: {json.dumps(upload_data, indent=2)}")
        doc_id = upload_data["id"]
        
        # Wait for background pipeline to complete
        print("\nAwaiting pipeline completion...")
        for _ in range(20):
            time.sleep(0.3)
            s_check = client.get(f"/api/v1/documents/{doc_id}/status").json()
            if s_check.get("status") in ["COMPLETED", "FAILED_VALIDATION", "FAILED_EXTRACTION"]:
                print(f"Pipeline reached state: {s_check.get('status')}")
                break

        # 2. GET /api/v1/documents/{id}
        print(f"\n--- 2. GET /api/v1/documents/{doc_id} ---")
        get_res = client.get(f"/api/v1/documents/{doc_id}")
        print(f"Status: {get_res.status_code}")
        print(f"Response: {json.dumps(get_res.json(), indent=2)}")

        # 3. GET /api/v1/documents/{id}/status
        print(f"\n--- 3. GET /api/v1/documents/{doc_id}/status ---")
        status_res = client.get(f"/api/v1/documents/{doc_id}/status")
        print(f"Status: {status_res.status_code}")
        print(f"Response: {json.dumps(status_res.json(), indent=2)}")

        # 4. GET /api/v1/documents/{id}/content
        print(f"\n--- 4. GET /api/v1/documents/{doc_id}/content ---")
        content_res = client.get(f"/api/v1/documents/{doc_id}/content")
        print(f"Status: {content_res.status_code}")
        print(f"Response: {json.dumps(content_res.json(), indent=2)}")

        # 5. GET /api/v1/documents/{id}/requirements
        print(f"\n--- 5. GET /api/v1/documents/{doc_id}/requirements ---")
        reqs_res = client.get(f"/api/v1/documents/{doc_id}/requirements")
        print(f"Status: {reqs_res.status_code}")
        print(f"Response: {json.dumps(reqs_res.json(), indent=2)}")

        # 6. POST /api/v1/documents/{id}/process
        print(f"\n--- 6. POST /api/v1/documents/{doc_id}/process ---")
        process_res = client.post(f"/api/v1/documents/{doc_id}/process")
        print(f"Status: {process_res.status_code}")
        print(f"Response: {json.dumps(process_res.json(), indent=2)}")

        # 7. POST /api/v1/specifications/text
        print("\n--- 7. POST /api/v1/specifications/text ---")
        text_payload = {
            "title": "Substation Induction Motor Schedule",
            "department": "Public Works & Power",
            "tender_reference": "TEND/2026/PWR/089",
            "target_product_name": "Electric Induction Motor",
            "raw_content": "The motor shall have a rated power of 5 kW. The operating temperature shall be -10 °C to 50 °C. The enclosure shall be IP55."
        }
        text_res = client.post("/api/v1/specifications/text", json=text_payload)
        print(f"Status: {text_res.status_code}")
        print(f"Response: {json.dumps(text_res.json(), indent=2)}")

        # Fetch requirements for the text spec
        text_doc_id = text_res.json().get("document_id")
        if text_doc_id:
            print(f"\n--- Requirements for Text Specification (Document {text_doc_id}) ---")
            text_reqs = client.get(f"/api/v1/documents/{text_doc_id}/requirements")
            print(f"Status: {text_reqs.status_code}")
            print(f"Response: {json.dumps(text_reqs.json(), indent=2)}")

if __name__ == "__main__":
    main()
