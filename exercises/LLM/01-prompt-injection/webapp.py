"""Browser UI for the Prompt Injection lab.

A zero-dependency web app (Python standard library only) that lets you run the
attacks live:

- See the bot's guardrail (system prompt).
- Fire any of the five preset attacks with one click.
- Type your own message.
- Watch a clear LEAK / SAFE verdict, with the leaked secret highlighted.

Run it:
    python3 webapp.py
then open http://localhost:8000 in your browser.
"""

from __future__ import annotations

import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from attacks import ATTACKS
from customercare_bot import SECRET_DISCOUNT_CODE, SYSTEM_PROMPT, respond
from defenses import respond_defended, describe_pattern
from judge import secret_leaked

HOST = "localhost"
PORT = 8000

# Appended to every "blocked" explanation. Learners almost always ask why real
# products do not just use a regex blocklist like this lab does. This answers
# that and points to real, production guardrail systems they can read about.
COMMERCIAL_GUARDRAILS_NOTE = (
    "For real systems (this is a learning lab): the rules here are simple "
    "regular expressions so you can SEE the idea clearly. Commercial assistants "
    "rarely rely on keyword matching alone, because an attacker can reword a "
    "payload in endless ways that no blocklist can list out in advance. "
    "Production guardrails instead use trained machine-learning classifiers "
    "that judge the MEANING and intent of a message, not just its exact words. "
    "They reason over embeddings and dedicated safety models, they run as "
    "separate services wrapped around the model so they can be improved without "
    "retraining it, and they are red-teamed and updated continuously as new "
    "attacks appear.\n\n"
    "A few real guardrail systems you can read about:\n"
    "- OWASP Top 10 for LLM Applications (LLM01 Prompt Injection): https://genai.owasp.org\n"
    "- Microsoft Azure AI Content Safety, Prompt Shields: https://learn.microsoft.com/en-us/azure/ai-services/content-safety/how-to-prompt-shields\n"
    "- Meta Llama Guard (an LLM that screens inputs and outputs): https://github.com/meta-llama/llama-guard\n"
    "- NVIDIA NeMo Guardrails: https://github.com/NVIDIA/NeMo-Guardrails\n"
    "- OpenAI Moderation guide: https://platform.openai.com/docs/guides/moderation\n\n"
    "The takeaway: the CONCEPT you just saw (check the input, check the output, "
    "keep the secret out of reach) is exactly what production systems do. They "
    "just do it with much smarter detectors than a regex."
)


def build_anatomy(message: str, reply: str, leaked: bool, attack: dict | None,
                  blocked_by: str | None = None, matched_pattern: str | None = None) -> dict:
    """Produce a stage-by-stage explanation of what just happened.

    Returns a dict the UI renders in the 'What just happened?' panel.
    """
    technique = attack["technique"] if attack else "Custom / free-form payload"
    if attack and attack.get("why"):
        why = attack["why"]
    else:
        why = (
            "This was a custom message. If the secret leaked, the model treated "
            "your text as an instruction that outranked its system rule. If it "
            "stayed safe, the wording did not override the guardrail this time. "
            "Try one of the preset techniques to compare."
        )

    if blocked_by == "input_guardrail":
        description = describe_pattern(matched_pattern) if matched_pattern else ""
        defense = attack.get("defense") if attack else None
        attack_mechanism = attack.get("description") if attack else None

        exploitation = (
            f"Blocked BEFORE the model. The guardrail matched the rule "
            f"/{matched_pattern}/ and recognized this as a '{technique}' attempt, "
            "so it refused without ever calling the model."
        )
        impact = "No leak. The guardrail layer stopped the attack at the door."

        parts = []
        if attack_mechanism:
            parts.append(f"How this attack tries to work: {attack_mechanism}")
        parts.append(
            "What the guardrail did: it ran the raw message through the "
            "regular-expression rules in defenses.py before the model was "
            f"called, and this rule fired:\n\n    /{matched_pattern}/\n\n"
            f"What that rule catches: {description}"
        )
        if defense:
            parts.append(f"Why that defeats THIS specific attack: {defense}")
        else:
            parts.append(
                "Because the match happens OUTSIDE the model, the payload is "
                "rejected before the model can be persuaded by anything in it."
            )
        parts.append(COMMERCIAL_GUARDRAILS_NOTE)
        why = "\n\n".join(parts)
    elif blocked_by == "output_guardrail":
        defense = attack.get("defense") if attack else None
        attack_mechanism = attack.get("description") if attack else None
        exploitation = (
            f"This '{technique}' attack slipped past the input filter and "
            "tricked the model into putting the secret in its reply. The output "
            "guardrail then scanned that reply, detected the secret, and replaced "
            "the whole thing with a safe refusal before you saw it."
        )
        impact = "No leak. The guardrail caught the secret on the way out."
        parts = []
        if attack_mechanism:
            parts.append(f"How this attack tries to work: {attack_mechanism}")
        parts.append(
            "What the guardrail did: the output guardrail runs the model's reply "
            "through the same leak detector used to score attacks (judge.py). It "
            "normalizes the text (collapses spaces and dashes, ignores case) and "
            "checks whether the secret is present."
        )
        parts.append(
            "Why that defeats THIS specific attack: it does not matter how the "
            "model was tricked or how cleverly the secret was formatted. If the "
            "secret appears anywhere in the response, the response is blocked. "
            "This is the backstop that catches novel payloads the input filter "
            "does not yet know about."
        )
        parts.append(COMMERCIAL_GUARDRAILS_NOTE)
        why = "\n\n".join(parts)
    elif leaked:
        exploitation = "The model followed the attacker's text instead of its system rule."
        impact = f"Secret leaked. The confidential code {SECRET_DISCOUNT_CODE} was exposed."
    else:
        exploitation = "The model resisted: it stuck to its system rule and refused."
        impact = "No leak. The confidential code stayed protected this time."

    return {
        "technique": technique,
        "why": why,
        "blocked_by": blocked_by,
        "matched_pattern": matched_pattern,
        "stages": [
            {
                "name": "1. Reconnaissance",
                "text": "The bot holds a confidential discount code and a rule never to reveal it.",
            },
            {
                "name": "2. Payload crafting",
                "text": f"Technique used: {technique}.",
            },
            {
                "name": "3. Delivery",
                "text": "The payload was sent as an ordinary chat message (untrusted user input).",
            },
            {
                "name": "4. Exploitation",
                "text": exploitation,
            },
            {
                "name": "5. Impact",
                "text": impact,
            },
        ],
    }

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prompt Injection Lab: Contoso CustomerCare Bot</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         margin: 0; background: #0f172a; color: #e2e8f0; }
  header { background: #1e293b; padding: 20px 28px; border-bottom: 1px solid #334155; }
  header h1 { margin: 0 0 4px; font-size: 20px; }
  header p { margin: 0; color: #94a3b8; font-size: 14px; }
  .wrap { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;
          max-width: 1500px; margin: 24px auto; padding: 0 20px; }
  @media (max-width: 1100px) { .wrap { grid-template-columns: 1fr; } }
  .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 18px; }
  .card h2 { margin: 0 0 12px; font-size: 15px; text-transform: uppercase;
             letter-spacing: .5px; color: #cbd5e1; }
  pre.sys { white-space: pre-wrap; background: #0b1220; border: 1px solid #334155;
            border-radius: 8px; padding: 12px; font-size: 12.5px; color: #cbd5e1; margin: 0; }
  .attacks { display: flex; flex-direction: column; gap: 8px; }
  button { font: inherit; cursor: pointer; border-radius: 8px; border: 1px solid #475569;
           background: #334155; color: #e2e8f0; padding: 10px 12px; text-align: left; }
  button:hover { background: #3f4f6b; }
  button .tech { display: block; font-weight: 600; }
  button .desc { display: block; font-size: 12px; color: #94a3b8; margin-top: 2px; }
  textarea { width: 100%; min-height: 70px; border-radius: 8px; border: 1px solid #475569;
             background: #0b1220; color: #e2e8f0; padding: 10px; font: inherit; resize: vertical; }
  .row { display: flex; gap: 8px; margin-top: 8px; }
  .row button.primary { background: #2563eb; border-color: #2563eb; text-align: center; flex: 1; }
  .row button.ghost { background: transparent; }
  .verdict { display: inline-block; padding: 4px 12px; border-radius: 999px; font-weight: 700;
             font-size: 13px; }
  .verdict.leak { background: #7f1d1d; color: #fecaca; }
  .verdict.safe { background: #14532d; color: #bbf7d0; }
  .verdict.idle { background: #334155; color: #cbd5e1; }
  .reply { white-space: pre-wrap; background: #0b1220; border: 1px solid #334155;
           border-radius: 8px; padding: 12px; margin-top: 12px; min-height: 60px; font-size: 14px; }
  mark { background: #f59e0b; color: #1f2937; padding: 0 3px; border-radius: 3px; font-weight: 700; }
  .muted { color: #94a3b8; font-size: 12px; }
  .spinner { color: #94a3b8; }
  .stage { border-left: 3px solid #475569; padding: 6px 0 6px 12px; margin: 0 0 10px; }
  .stage.hit { border-left-color: #ef4444; }
  .stage.safe { border-left-color: #22c55e; }
  .stage .sname { font-weight: 700; font-size: 13px; color: #e2e8f0; }
  .stage .stext { font-size: 13px; color: #cbd5e1; margin-top: 2px; }
  .why { background: #0b1220; border: 1px solid #334155; border-radius: 8px;
         padding: 12px; font-size: 13px; line-height: 1.5; color: #e2e8f0; margin-top: 12px;
         white-space: pre-wrap; }
  .why h3 { margin: 0 0 6px; font-size: 12px; text-transform: uppercase;
            letter-spacing: .5px; color: #f59e0b; }
  .why a { color: #93c5fd; }
  .tech-label { font-size: 13px; color: #93c5fd; margin: 0 0 12px; font-weight: 600; }
  .switch { display: inline-flex; align-items: center; gap: 8px; margin-top: 12px;
            font-size: 13px; color: #cbd5e1; cursor: pointer; }
  .switch input { width: 16px; height: 16px; }
  .switch b { color: #f87171; }
  .switch.on b { color: #4ade80; }
  .verdict.blocked { background: #1e3a8a; color: #bfdbfe; }
</style>
</head>
<body>
<header>
  <h1>Prompt Injection Lab: Contoso CustomerCare Bot</h1>
  <p>The bot below is told to protect a secret discount code. Try to make it leak. (OWASP LLM01)</p>
  <label class="switch">
    <input type="checkbox" id="defense">
    <span>Defense layer (guardrails): <b id="defstate">OFF</b></span>
  </label>
</header>

<div class="wrap">
  <section class="card">
    <h2>1. The guardrail (system prompt)</h2>
    <pre class="sys" id="sys"></pre>
    <p class="muted" style="margin-top:12px">2. Pick an attack, or write your own message:</p>
    <div class="attacks" id="attacks"></div>
  </section>

  <section class="card">
    <h2>3. Send a message</h2>
    <textarea id="msg" placeholder="Type a message to the bot..."></textarea>
    <div class="row">
      <button class="primary" id="send">Send</button>
      <button class="ghost" id="clear">Clear</button>
    </div>
    <div style="margin-top:16px">
      <span class="verdict idle" id="verdict">No message sent yet</span>
    </div>
    <div class="reply" id="reply"><span class="muted">The bot's reply will appear here.</span></div>
  </section>

  <section class="card">
    <h2>4. What just happened?</h2>
    <p class="tech-label" id="tech"></p>
    <div id="stages"><span class="muted">Send a message to see a stage-by-stage breakdown of the attack.</span></div>
    <div class="why" id="why" style="display:none"><h3>Why it works</h3><span id="whytext"></span></div>
  </section>
</div>

<script>
const SECRET = %SECRET_JSON%;
let attacks = [];
let currentAttackId = null;

function esc(s){ return s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

function highlight(text){
  // Escape, then highlight the secret (case-insensitive) so leaks pop visually.
  let html = esc(text);
  const re = new RegExp(esc(SECRET).replace(/[-]/g,'\\\\-?\\\\s*'), 'ig');
  return html.replace(re, m => '<mark>' + m + '</mark>');
}

async function load(){
  const r = await fetch('/api/info');
  const info = await r.json();
  document.getElementById('sys').textContent = info.system_prompt;
  attacks = info.attacks;
  const box = document.getElementById('attacks');
  attacks.forEach(a => {
    const b = document.createElement('button');
    b.innerHTML = '<span class="tech">' + esc(a.technique) + '</span>' +
                  '<span class="desc">' + esc(a.description) + '</span>';
    b.onclick = () => { document.getElementById('msg').value = a.payload; currentAttackId = a.id; send(); };
    box.appendChild(b);
  });
}

function renderAnatomy(anatomy){
  document.getElementById('tech').textContent = 'Technique: ' + anatomy.technique;
  const stages = document.getElementById('stages');
  stages.innerHTML = '';
  anatomy.stages.forEach((s, i) => {
    const d = document.createElement('div');
    let cls = 'stage';
    if(i === anatomy.stages.length - 1){
      cls += anatomy.leaked ? ' hit' : ' safe';
    } else if(i === 3 && anatomy.blocked_by){
      cls += ' safe';  // exploitation stage was stopped by a guardrail
    }
    d.className = cls;
    d.innerHTML = '<div class="sname">' + esc(s.name) + '</div>' +
                  '<div class="stext">' + esc(s.text) + '</div>';
    stages.appendChild(d);
  });
  const whyHtml = esc(anatomy.why).replace(
    /(https?:\/\/[^\s]+)/g,
    '<a href="$1" target="_blank" rel="noopener">$1</a>'
  );
  document.getElementById('whytext').innerHTML = whyHtml;
  document.getElementById('why').style.display = 'block';
}

async function send(){
  const msg = document.getElementById('msg').value.trim();
  if(!msg) return;
  const verdict = document.getElementById('verdict');
  const reply = document.getElementById('reply');
  verdict.className = 'verdict idle'; verdict.textContent = 'Asking the model...';
  reply.innerHTML = '<span class="spinner">Thinking...</span>';
  try {
    const r = await fetch('/api/ask', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({message: msg, attack_id: currentAttackId, defended: document.getElementById('defense').checked})
    });
    const data = await r.json();
    reply.innerHTML = highlight(data.reply);
    if(data.leaked){
      verdict.className = 'verdict leak'; verdict.textContent = 'LEAK: secret revealed!';
    } else if(data.blocked_by){
      const where = data.blocked_by === 'input_guardrail' ? 'input guardrail' : 'output guardrail';
      verdict.className = 'verdict blocked'; verdict.textContent = 'BLOCKED by ' + where;
    } else {
      verdict.className = 'verdict safe'; verdict.textContent = 'SAFE: secret protected';
    }
    if(data.anatomy){ data.anatomy.leaked = data.leaked; renderAnatomy(data.anatomy); }
  } catch(e){
    verdict.className = 'verdict idle'; verdict.textContent = 'Error';
    reply.textContent = String(e);
  }
}

document.getElementById('send').onclick = () => { send(); };
document.getElementById('defense').addEventListener('change', (e) => {
  const on = e.target.checked;
  document.getElementById('defstate').textContent = on ? 'ON' : 'OFF';
  document.querySelector('.switch').classList.toggle('on', on);
});
document.getElementById('msg').addEventListener('input', () => { currentAttackId = null; });
document.getElementById('clear').onclick = () => {
  document.getElementById('msg').value = '';
  currentAttackId = null;
  document.getElementById('reply').innerHTML = '<span class="muted">The bot\\'s reply will appear here.</span>';
  const v = document.getElementById('verdict'); v.className = 'verdict idle'; v.textContent = 'No message sent yet';
  document.getElementById('tech').textContent = '';
  document.getElementById('stages').innerHTML = '<span class="muted">Send a message to see a stage-by-stage breakdown of the attack.</span>';
  document.getElementById('why').style.display = 'none';
};
load();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, obj: dict) -> None:
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json")

    def do_GET(self) -> None:  # noqa: N802 (required name)
        if self.path in ("/", "/index.html"):
            html = PAGE.replace("%SECRET_JSON%", json.dumps(SECRET_DISCOUNT_CODE))
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
        elif self.path == "/api/info":
            self._send_json(200, {
                "system_prompt": SYSTEM_PROMPT,
                "attacks": [
                    {
                        "id": a["id"],
                        "technique": a["technique"],
                        "description": a["description"],
                        "payload": a["payload"],
                    }
                    for a in ATTACKS
                ],
            })
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802 (required name)
        if self.path != "/api/ask":
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            message = str(payload.get("message", "")).strip()
            attack_id = payload.get("attack_id")
            defended = bool(payload.get("defended"))
            if not message:
                self._send_json(400, {"error": "empty message"})
                return
            attack = None
            if attack_id:
                attack = next((a for a in ATTACKS if a["id"] == attack_id), None)

            if defended:
                result = respond_defended(message)
                reply = result.reply
                leaked = secret_leaked(reply)
                blocked_by = result.blocked_by
                matched_pattern = result.matched_pattern
            else:
                reply = respond(message)
                leaked = secret_leaked(reply)
                blocked_by = None
                matched_pattern = None

            self._send_json(200, {
                "reply": reply,
                "leaked": leaked,
                "defended": defended,
                "blocked_by": blocked_by,
                "matched_pattern": matched_pattern,
                "anatomy": build_anatomy(message, reply, leaked, attack, blocked_by, matched_pattern),
            })
        except Exception as exc:  # surface a clean error to the UI
            self._send_json(500, {"error": str(exc)})

    def log_message(self, *args) -> None:  # keep the console quiet while running
        pass


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print(f"Prompt Injection lab running at {url}")
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
