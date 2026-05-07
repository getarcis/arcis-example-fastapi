# arcis-example-fastapi

> Minimal FastAPI + Arcis app. One install, one middleware registration, twenty-plus attack vectors blocked.

## What this is

The smallest possible demo of Arcis on FastAPI. Two files:

- [`main.py`](./main.py) — FastAPI app with `app.add_middleware(ArcisMiddleware, block=True)` as the only security line.
- [`attack.py`](./attack.py) — fires 8 attack payloads at the running server and reports which ones Arcis blocks.

Total dependencies: `arcis` + `fastapi` + `uvicorn` + `httpx` (httpx for the attack script only).

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
