"""Local web server for the Bots Protection demo (Cloudflare Turnstile).

It serves the single page app and exposes one endpoint, /verify, which performs
the SERVER SIDE half of Turnstile: it sends the token from the browser to
Cloudflare's Siteverify API and returns the result.

By default it uses Cloudflare's public TEST secret key, so the whole thing runs
with no Cloudflare account. To verify against your own real widget, set the
environment variable TURNSTILE_SECRET to your real secret key and the page's
Advanced panel will route through it.

Standard library only. Needs outbound internet to reach Cloudflare.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "localhost"
PORT = 8001

SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

# Cloudflare's public test secret keys (safe to ship, documented for testing).
# The pass key approves any token, the fail key rejects any token. A real
# deployment uses one real secret that decides per token.
TEST_PASS_SECRET = "1x0000000000000000000000000000000AA"
TEST_FAIL_SECRET = "2x0000000000000000000000000000000AA"

HERE = os.path.dirname(os.path.abspath(__file__))


def siteverify(token: str, secret: str, timeout: int = 15) -> dict:
    """Call Cloudflare Siteverify and return the parsed JSON response."""
    data = urllib.parse.urlencode({"secret": secret, "response": token}).encode("utf-8")
    request = urllib.request.Request(SITEVERIFY_URL, data=data)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def choose_secret(use_real: bool, simulate: str | None = None) -> tuple[str, str | None]:
    """Pick the secret to validate with. Returns (secret, error).

    use_real        validate against your own real widget (env TURNSTILE_SECRET).
    simulate=reject  use the fail test key to mirror Cloudflare rejecting a
                     forged token that never passed the widget.
    otherwise        use the pass test key (normal success path).
    """
    if use_real:
        secret = os.environ.get("TURNSTILE_SECRET", "").strip()
        if not secret:
            return "", "TURNSTILE_SECRET is not set, cannot verify against a real widget."
        return secret, None
    if simulate == "reject":
        return TEST_FAIL_SECRET, None
    return TEST_PASS_SECRET, None


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: dict) -> None:
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json")

    def do_GET(self):  # noqa: N802
        if self.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as handle:
                self._send(200, handle.read(), "text/html; charset=utf-8")
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/verify":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            token = str(payload.get("token", "")).strip()
            use_real = bool(payload.get("real"))
            simulate = payload.get("simulate")
            if not token:
                self._json(400, {"error": "missing token"})
                return
            secret, error = choose_secret(use_real, simulate)
            if error:
                self._json(200, {"verified": False, "server_note": error, "cloudflare": None})
                return
            result = siteverify(token, secret)
            note = None
            if simulate == "reject":
                note = ("Simulated a bot that skipped the widget. In production your one "
                        "real secret key makes this call, and Cloudflare rejects a token "
                        "that never passed the browser check, exactly like this.")
            self._json(200, {
                "verified": bool(result.get("success")),
                "server_note": note,
                "cloudflare": result,
            })
        except Exception as exc:
            self._json(200, {
                "verified": False,
                "server_note": f"Could not reach Cloudflare Siteverify: {exc}",
                "cloudflare": None,
            })

    def log_message(self, *args):
        pass


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print(f"Bots Protection demo running at {url}")
    print("Press Ctrl+C to stop.")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
        server.shutdown()


if __name__ == "__main__":
    main()
