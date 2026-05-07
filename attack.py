"""Fire 8 attack payloads at the running FastAPI server and report
which ones Arcis blocks. Run after starting the server with
``uvicorn main:app --reload``. Expected: every attack returns 403,
every safe payload returns 200.
"""

import os
import sys

import httpx

BASE = os.environ.get("BASE_URL", "http://localhost:8000")

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def safe_call() -> httpx.Response:
    return httpx.get(f"{BASE}/api/echo", params={"q": "hello"})


def xss_query() -> httpx.Response:
    return httpx.get(f"{BASE}/api/echo", params={"q": "<script>alert(1)</script>"})


def xss_event_handler() -> httpx.Response:
    return httpx.post(f"{BASE}/api/echo", json={"x": '<img onerror="alert(1)">'})


def sql_injection() -> httpx.Response:
    return httpx.get(f"{BASE}/api/echo", params={"q": "'; DROP TABLE users; --"})


def nosql_operator() -> httpx.Response:
    return httpx.post(f"{BASE}/api/echo", json={"q": {"$gt": ""}})


def path_traversal() -> httpx.Response:
    return httpx.get(f"{BASE}/api/echo", params={"file": "../../etc/passwd"})


def command_injection() -> httpx.Response:
    return httpx.get(f"{BASE}/api/echo", params={"cmd": "hi; rm -rf /"})


def ssti() -> httpx.Response:
    return httpx.get(f"{BASE}/api/echo", params={"t": "{{7*7}}"})


def xxe() -> httpx.Response:
    return httpx.post(
        f"{BASE}/api/echo",
        json={"xml": '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>'},
    )


TESTS = [
    ("safe", "safe input", safe_call, 200),
    ("xss", "<script> in query", xss_query, 403),
    ("xss", "event handler", xss_event_handler, 403),
    ("sql", "'; DROP TABLE users; --", sql_injection, 403),
    ("nosql", '{ "$gt": "" } operator', nosql_operator, 403),
    ("path", "../../etc/passwd", path_traversal, 403),
    ("command", "; rm -rf /", command_injection, 403),
    ("ssti", "Jinja2 {{7*7}}", ssti, 403),
    ("xxe", "DOCTYPE ENTITY", xxe, 403),
]


def main() -> int:
    print(f"\nArcis attack demo against {BASE}\n{'-' * 64}")
    blocked = 0
    allowed = 0
    unexpected = 0
    for category, label, send, expected in TESTS:
        try:
            res = send()
        except httpx.RequestError as err:
            print(f"{RED}ERR{RESET}    {category:<8} {label}: {err}")
            unexpected += 1
            continue
        if res.status_code == expected:
            verb = "OK   " if expected == 200 else "BLOCK"
            color = GREEN
            note = "passed through" if expected == 200 else "Arcis denied"
            print(f"{color}{verb}{RESET}  {category:<8} {label}: {res.status_code} ({note}, as expected)")
            if expected == 200:
                allowed += 1
            else:
                blocked += 1
        else:
            label_word = "WHAT" if expected == 200 else "LEAK"
            print(f"{RED}{label_word}{RESET}   {category:<8} {label}: got {res.status_code}, expected {expected}")
            unexpected += 1
    print("-" * 64)
    print(f"{GREEN}{blocked} attack{'s' if blocked != 1 else ''} blocked{RESET}, "
          f"{allowed} safe call{'s' if allowed != 1 else ''} passed, "
          f"{YELLOW}{unexpected} unexpected{RESET}")
    return 0 if unexpected == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
