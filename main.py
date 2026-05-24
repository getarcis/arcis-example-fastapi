"""Minimal FastAPI + Arcis app.

One install (`pip install arcis`), one middleware registration, and the
full Arcis sanitizer pipeline (XSS, SQL, NoSQL, path, command, SSTI,
XXE, prompt injection, prototype, LDAP, XPath, header injection) plus
rate limiting + security headers is gated against your route handler.
Bot detection, CSRF, CORS, cookies, URL / redirect / file validation,
and error scrubbing are deliberate opt-ins on separate middleware. See
README for the full "does / does not do" table.

Run with ``uvicorn main:app --reload``, then fire ``python attack.py``
in another shell.
"""

from fastapi import FastAPI, Request
from arcis.fastapi import ArcisMiddleware

app = FastAPI()

# block=True returns 403 on detected attacks. The default is sanitize
# (silently strip + observe), which is safer to roll out without
# breaking existing clients. We use block here so the demo is visible.
app.add_middleware(ArcisMiddleware, block=True)


@app.get("/")
def root():
    return {"ok": True, "message": "Arcis is live. Try /api/echo with an attack payload."}


@app.get("/api/echo")
def echo_get(request: Request):
    return {"query": dict(request.query_params)}


@app.post("/api/echo")
async def echo_post(request: Request):
    body = await request.json()
    return {"received": body}
