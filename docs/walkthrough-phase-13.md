# Phase 13: Security Hardening, Rate Limiting & Guardrails Engine — Walkthrough

## Overview
Phase 13 delivers security hardening, sliding-window rate limiting, AST sandbox sandboxing, adversarial prompt injection detection, and PII masking across AI PlacementOS.

### Key Architectural Capabilities
1. **Sliding Window Token Bucket Rate Limiter** ([apps/api/app/core/rate_limiter.py](file:///c:/Users/PRANESH.M/OneDrive/Desktop/AI%20PlacementOS/apps/api/app/core/rate_limiter.py)):
   - In-memory sliding window calculating remaining request quota and exact reset timestamps.
   - Injects standard headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`.
2. **AI & Sandbox Security Guardrails** ([apps/api/app/core/guardrails.py](file:///c:/Users/PRANESH.M/OneDrive/Desktop/AI%20PlacementOS/apps/api/app/core/guardrails.py)):
   - **AST Code Inspection**: Validates submitted Python code in the DSA sandbox, blocking dangerous imports (`os`, `subprocess`, `sys`, `socket`, `shutil`) and execution calls (`eval`, `exec`, `open`, `__import__`).
   - **Adversarial Prompt Injection Scanner**: Flags jailbreak attempts, system prompt exfiltration, and safety bypass instructions.
   - **PII Masking**: Sanitizes credit card numbers, SSNs, and API keys (`sk-...`, `ghp_...`).
3. **Security Response Headers Middleware** ([apps/api/app/main.py](file:///c:/Users/PRANESH.M/OneDrive/Desktop/AI%20PlacementOS/apps/api/app/main.py)):
   - Enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Strict-Transport-Security`.
4. **Security Event Audit Logging** ([apps/api/app/models/security_audit.py](file:///c:/Users/PRANESH.M/OneDrive/Desktop/AI%20PlacementOS/apps/api/app/models/security_audit.py)):
   - Records violation telemetry and provides admin auditing endpoints at `/api/v1/security/audit-logs` and `/api/v1/security/guardrail-check`.

---

## Verification Results

### Backend Pytest Suite
- **101/101 tests passing** across the entire backend:
  - `tests/test_rate_limiter.py`
  - `tests/test_security_guardrails.py`
  - `tests/test_security_audit.py`
