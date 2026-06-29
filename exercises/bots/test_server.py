"""Tests for the Bots Protection demo server.

Layer 1 (deterministic): the secret selection logic and the /verify endpoint
with Siteverify mocked, so these always run.

Layer 2 (live): hits Cloudflare Siteverify with the documented dummy token.
Skipped automatically if the network is unreachable.

Run:
    python3 -m unittest -v
"""

from __future__ import annotations

import json
import os
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest import mock

import server


def _internet_ok() -> bool:
    try:
        server.siteverify("XXXX.DUMMY.TOKEN.XXXX", server.TEST_PASS_SECRET, timeout=8)
        return True
    except Exception:
        return False


class TestSecretSelection(unittest.TestCase):
    def test_default_uses_test_secret(self):
        secret, error = server.choose_secret(use_real=False)
        self.assertEqual(secret, server.TEST_PASS_SECRET)
        self.assertIsNone(error)

    def test_real_without_env_returns_error(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            secret, error = server.choose_secret(use_real=True)
        self.assertEqual(secret, "")
        self.assertIsNotNone(error)

    def test_real_with_env_uses_it(self):
        with mock.patch.dict(os.environ, {"TURNSTILE_SECRET": "my-real-secret"}):
            secret, error = server.choose_secret(use_real=True)
        self.assertEqual(secret, "my-real-secret")
        self.assertIsNone(error)

    def test_simulate_reject_uses_fail_secret(self):
        secret, error = server.choose_secret(use_real=False, simulate="reject")
        self.assertEqual(secret, server.TEST_FAIL_SECRET)
        self.assertIsNone(error)


def _start(handler) -> tuple[ThreadingHTTPServer, int]:
    httpd = ThreadingHTTPServer(("localhost", 0), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def _post(port: int, path: str, obj: dict):
    req = urllib.request.Request(
        f"http://localhost:{port}{path}",
        data=json.dumps(obj).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read())


class TestVerifyEndpointMocked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd, cls.port = _start(server.Handler)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_missing_token_is_400(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            _post(self.port, "/verify", {"token": ""})
        self.assertEqual(ctx.exception.code, 400)
        ctx.exception.close()

    def test_verified_true_when_cloudflare_succeeds(self):
        fake = {"success": True, "challenge_ts": "now", "hostname": "localhost", "error-codes": []}
        with mock.patch.object(server, "siteverify", return_value=fake):
            status, data = _post(self.port, "/verify", {"token": "XXXX.DUMMY.TOKEN.XXXX"})
        self.assertEqual(status, 200)
        self.assertTrue(data["verified"])
        self.assertEqual(data["cloudflare"]["hostname"], "localhost")

    def test_verified_false_when_cloudflare_fails(self):
        fake = {"success": False, "error-codes": ["invalid-input-response"]}
        with mock.patch.object(server, "siteverify", return_value=fake):
            status, data = _post(self.port, "/verify", {"token": "anything"})
        self.assertFalse(data["verified"])

    def test_unreachable_cloudflare_is_handled(self):
        with mock.patch.object(server, "siteverify", side_effect=OSError("no network")):
            status, data = _post(self.port, "/verify", {"token": "x"})
        self.assertEqual(status, 200)
        self.assertFalse(data["verified"])
        self.assertIn("Could not reach", data["server_note"])


@unittest.skipUnless(_internet_ok(), "Cloudflare Siteverify is not reachable")
class TestLiveSiteverify(unittest.TestCase):
    def test_dummy_token_passes_with_pass_secret(self):
        result = server.siteverify("XXXX.DUMMY.TOKEN.XXXX", server.TEST_PASS_SECRET)
        self.assertTrue(result.get("success"))

    def test_fail_secret_rejects_token(self):
        # The fail test key models Cloudflare rejecting a token. This is what
        # the "bot bypass" simulation routes through.
        result = server.siteverify("XXXX.DUMMY.TOKEN.XXXX", server.TEST_FAIL_SECRET)
        self.assertFalse(result.get("success"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
