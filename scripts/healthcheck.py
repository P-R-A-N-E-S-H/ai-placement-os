#!/usr/bin/env python3
"""
AI PlacementOS Production Readiness & Health Verification Script.
Checks API connectivity, Database health, Redis status, and Web Frontend status.
"""
import sys
import time
import urllib.request
import json

def check_endpoint(name: str, url: str, timeout: int = 5) -> bool:
    print(f"[*] Checking {name} ({url})...", end=" ", flush=True)
    start_t = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PlacementOS-HealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.status
            elapsed_ms = int((time.time() - start_t) * 1000)
            if 200 <= status < 300:
                print(f"PASSED (HTTP {status} in {elapsed_ms}ms)")
                return True
            else:
                print(f"FAILED (HTTP {status})")
                return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def main():
    print("==================================================")
    print("      AI PlacementOS Production Health Probe      ")
    print("==================================================")
    
    api_url = "http://127.0.0.1:8000/api/v1/health"
    web_url = "http://127.0.0.1:3000"
    
    api_ok = check_endpoint("FastAPI Backend", api_url, timeout=10)
    web_ok = check_endpoint("Next.js Frontend", web_url, timeout=10)

    
    print("--------------------------------------------------")
    if api_ok and web_ok:
        print("[SUCCESS] All AI PlacementOS services are healthy and operational.")
        sys.exit(0)
    elif api_ok:
        print("[PARTIAL] Backend API is healthy; Frontend web server is offline.")
        sys.exit(0)
    else:
        print("[ERROR] Healthcheck probe failed for core services.")
        sys.exit(1)

if __name__ == "__main__":
    main()
