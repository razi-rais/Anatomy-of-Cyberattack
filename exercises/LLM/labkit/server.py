"""Generic web server for the lab kit.

It serves the shared UI and a small JSON API. The server itself knows nothing
about any specific attack. Each exercise registers a module object that provides
its scenario, its attack buttons, and an ``ask`` method. This keeps the server
generic and lets the dropdown switch between exercises in one running process.

Run through exercises/serve.py, which registers the modules and starts this.
"""

from __future__ import annotations

import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from labkit.ollama import DEFAULT_MODEL, get_model_info
from labkit.ui import PAGE

HOST = "localhost"
PORT = 8000


def module_summary(module) -> dict:
    return {"id": module.id, "title": module.title, "owasp": module.owasp}


def module_info(module) -> dict:
    return {
        "id": module.id,
        "title": module.title,
        "owasp": module.owasp,
        "intro": module.intro,
        "context": getattr(module, "context", ""),
        "flow": list(getattr(module, "flow", [])),
        "scenario_title": module.scenario_title,
        "scenario": module.scenario,
        "trusted_instruction": getattr(module, "trusted_instruction", ""),
        "tools": list(getattr(module, "tools", [])),
        "note": getattr(module, "note", ""),
        "input_title": module.input_title,
        "input_label": module.input_label,
        "input_placeholder": module.input_placeholder,
        "success_label": module.success_label,
        "safe_label": module.safe_label,
        "highlights": list(getattr(module, "highlights", [])),
        "attacks": [
            {
                "id": a["id"],
                "technique": a["technique"],
                "description": a["description"],
                "payload": a["payload"],
            }
            for a in module.attacks
        ],
    }


def make_handler(modules: list, model: str):
    registry = {m.id: m for m in modules}

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
                self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            elif self.path == "/api/modules":
                self._json(200, {
                    "modules": [module_summary(m) for m in modules],
                    "model": get_model_info(model),
                })
            elif self.path.startswith("/api/module/"):
                module_id = self.path[len("/api/module/"):]
                module = registry.get(module_id)
                if not module:
                    self._json(404, {"error": "unknown module"})
                    return
                self._json(200, module_info(module))
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self):  # noqa: N802
            if not (self.path.startswith("/api/module/") and self.path.endswith("/ask")):
                self._json(404, {"error": "not found"})
                return
            module_id = self.path[len("/api/module/"):-len("/ask")]
            module = registry.get(module_id)
            if not module:
                self._json(404, {"error": "unknown module"})
                return
            length = int(self.headers.get("Content-Length", 0))
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
                message = str(payload.get("message", "")).strip()
                attack_id = payload.get("attack_id")
                defended = bool(payload.get("defended"))
                if not message:
                    self._json(400, {"error": "empty message"})
                    return
                result = module.ask(message, attack_id, defended)
                self._json(200, result)
            except Exception as exc:
                self._json(500, {"error": str(exc)})

        def log_message(self, *args):
            pass

    return Handler


def serve(modules: list, model: str = DEFAULT_MODEL, open_browser: bool = True) -> None:
    handler = make_handler(modules, model)
    server = ThreadingHTTPServer((HOST, PORT), handler)
    url = f"http://{HOST}:{PORT}"
    print(f"Lab kit running at {url}")
    print("Press Ctrl+C to stop.")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
        server.shutdown()
