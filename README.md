# arcis-example-fastapi

[![CI](https://github.com/getarcis/arcis-example-fastapi/actions/workflows/ci.yml/badge.svg)](https://github.com/getarcis/arcis-example-fastapi/actions/workflows/ci.yml)

> Minimal FastAPI + Arcis app. One install, one middleware registration, the full Arcis sanitizer pipeline gated against your route handler.

## What this is

The smallest possible demo of Arcis on FastAPI. Two files:

- [`main.py`](./main.py): FastAPI app with `app.add_middleware(ArcisMiddleware, block=True)` as the only security line.
- [`attack.py`](./attack.py): fires 8 attack payloads at the running server and reports which ones Arcis blocks.

Total dependencies: `arcis` + `fastapi` + `uvicorn` + `httpx` (httpx for the attack script only).

## What this adapter does and does not do

| Protection | `ArcisMiddleware(block=True)` | Where to get it |
|---|---|---|
| Input sanitization (XSS, SQL, NoSQL, path, command, SSTI, XXE, prompt injection, prototype, LDAP, XPath, header injection) | yes | built in |
| Rate limiting (per-IP, in-memory; configurable to Redis) | yes | built in |
| Security headers (CSP, HSTS, X-Frame-Options, etc.) | yes | built in |
| Bot detection | no (opt-in) | `from arcis.middleware import bot_detection` |
| CSRF protection | no (opt-in) | `from arcis.middleware import csrf` |
| CORS | no (opt-in) | FastAPI's `CORSMiddleware`, or `from arcis.middleware import cors` |
| Secure cookies | no (opt-in) | `from arcis.middleware import secure_cookies` |
| URL / redirect / file-upload validation | no (opt-in) | `validate_url_ssrf`, `validate_redirect`, `validate_file_upload` from `arcis.validation` |
| Error-leakage scrubbing | no (opt-in) | `from arcis.middleware import error_handler` |

The 8-payload `attack.py` exercises only what `ArcisMiddleware(block=True)` ships out of the box. CSRF / CORS / cookies / bot / validation / error-scrub are deliberate opt-ins because every project enables them on different paths.

## Run it

```bash
pip install -r requirements.txt
uvicorn main:app --reload   # listens on http://localhost:8000
python attack.py            # in another shell — fires the demo payloads
```

Expected output:

```
Arcis attack demo against http://localhost:8000
----------------------------------------------------------------
OK     safe     safe input: 200 (passed through, as expected)
BLOCK  xss      <script> in query: 403 (Arcis denied, as expected)
BLOCK  xss      event handler: 403 (Arcis denied, as expected)
BLOCK  sql      '; DROP TABLE users; --: 403 (Arcis denied, as expected)
BLOCK  nosql    { "$gt": "" } operator: 403 (Arcis denied, as expected)
BLOCK  path     ../../etc/passwd: 403 (Arcis denied, as expected)
BLOCK  command  ; rm -rf /: 403 (Arcis denied, as expected)
BLOCK  ssti     Jinja2 {{7*7}}: 403 (Arcis denied, as expected)
BLOCK  xxe      DOCTYPE ENTITY: 403 (Arcis denied, as expected)
----------------------------------------------------------------
8 attacks blocked, 1 safe call passed, 0 unexpected
```

## How it works

1. `app.add_middleware(ArcisMiddleware, block=True)` registers the full Arcis middleware stack: sanitization, security headers, rate limiting, and the deny path that returns 403 on attack patterns.
2. Each request flows through Arcis before reaching your route handler.
3. Safe input (the first test) passes through unchanged. Attack payloads (the rest) are detected, blocked at the boundary, and never see the handler.

## Production rollout note

This example uses `block=True` so the demo is visible. In production, the safer rollout pattern is to start in the default sanitize-and-observe mode, watch the logs to confirm there are no false positives on real traffic, then flip `block=True`. See the [Arcis docs](https://gagancm.github.io/arcis/documentation/configuration.html) for the full configuration surface.

For multi-framework demos: see [arcis-example-express](https://github.com/getarcis/arcis-example-express), [arcis-example-nextjs](https://github.com/getarcis/arcis-example-nextjs), [arcis-example-gin](https://github.com/getarcis/arcis-example-gin), [arcis-example-bun](https://github.com/getarcis/arcis-example-bun).

## License

MIT.
