# NORMVAULT API Conventions & Contracts

This document governs the REST API architecture between the FastAPI backend and consumer applications (Vite frontend, CLI utilities, and third-party procurement integrations such as GeM).

---

## 1. Base URL & Versioning

- All production API endpoints must be prefixed with the version identifier:
  `/api/v1`
- Canonical root info:
  `GET /` → returns service name, version, and documentation links.
- Interactive OpenAPI documentation:
  `GET /api/v1/docs` (Swagger UI)
  `GET /api/v1/redoc` (ReDoc)

---

## 2. Standard Endpoints & Namespaces

| Namespace | Path | Method | Description | Phase |
| :--- | :--- | :--- | :--- | :--- |
| **Health** | `/api/v1/health` | `GET` | System, database, and pgvector diagnostics | Phase 0 |
| **Standards** | `/api/v1/standards/` | `GET` | List verified Indian Standards from DB | Phase 0 |
| **Standards** | `/api/v1/standards/{std_no}` | `GET` | Retrieve single standard with editions & amendments | Phase 1 |
| **Documents** | `/api/v1/documents/upload` | `POST` | Upload PDF/DOCX tender schedule | Phase 1 |
| **Analysis** | `/api/v1/analysis/extract` | `POST` | Extract structured parameters from text | Phase 2 |
| **Recommendations** | `/api/v1/recommendations/generate` | `POST` | Hybrid retrieval & explainable recommendation | Phase 3 |
| **Compliance** | `/api/v1/compliance/qco-check/{std_no}` | `GET` | Validate mandatory QCO statutory status | Phase 4 |

---

## 3. Unified Error Envelope

All non-2xx HTTP responses follow a strict envelope format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR | NOT_FOUND | INTERNAL_SERVER_ERROR | NOT_IMPLEMENTED",
    "message": "Human-readable explanation of the error condition.",
    "details": [ ... ]
  }
}
```

### HTTP Status Codes
- `200 OK`: Request succeeded.
- `201 Created`: Resource created successfully.
- `400 Bad Request`: Client submitted malformed parameters.
- `422 Unprocessable Entity`: Payload failed Pydantic validation constraints.
- `501 Not Implemented`: Endpoint planned for future phases (avoids serving fake data).
- `500 Internal Server Error`: Unexpected server failure.

---

## 4. Strict No Fake Data Constraint

- Endpoints must NEVER return synthetic Indian Standards, hallucinated amendments, or fictional compliance determinations.
- If no verified standards match a search or catalog query, the API returns an empty list (`[]`) with HTTP 200 rather than mock fallbacks.
