"""The shared browser UI for the lab kit.

A single page that works for any registered exercise. A dropdown at the top lets
the learner switch modules. The layout is the same three columns for every
exercise: the scenario plus attack buttons, the message box plus verdict and
reply, and the "What just happened?" anatomy panel. An expandable model info
panel shows which model is running, its size, and the token usage of the last
request.
"""

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anatomy of an LLM Attack: hands-on labs</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         margin: 0; background: #0f172a; color: #e2e8f0; }
  header { background: #1e293b; padding: 18px 28px; border-bottom: 1px solid #334155; }
  header h1 { margin: 0 0 10px; font-size: 19px; }
  .controls { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }
  select { font: inherit; background: #0b1220; color: #e2e8f0; border: 1px solid #475569;
           border-radius: 8px; padding: 8px 10px; }
  .owasp { font-size: 12px; color: #94a3b8; }
  .switch { display: inline-flex; align-items: center; gap: 8px; font-size: 13px;
            color: #cbd5e1; cursor: pointer; }
  .switch input { width: 16px; height: 16px; }
  .switch b { color: #f87171; }
  .switch.on b { color: #4ade80; }
  details.model { margin-left: auto; font-size: 12px; color: #cbd5e1; }
  details.model summary { cursor: pointer; color: #93c5fd; }
  details.model .grid { margin-top: 8px; display: grid; grid-template-columns: auto auto;
            gap: 2px 14px; background: #0b1220; border: 1px solid #334155;
            border-radius: 8px; padding: 10px; }
  details.model .k { color: #94a3b8; }
  .intro { max-width: 1500px; margin: 16px auto 0; padding: 0 20px; color: #cbd5e1; font-size: 14px; }
  .ctxwrap { max-width: 1500px; margin: 14px auto 0; padding: 0 20px; }
  .flow { display: flex; flex-wrap: wrap; align-items: stretch; gap: 8px; margin-bottom: 12px; }
  .flow .step { display: flex; align-items: center; background: #0b1220; border: 1px solid #334155;
                border-radius: 8px; padding: 8px 12px; font-size: 12.5px; color: #e2e8f0; max-width: 230px; }
  .flow .step.start { border-color: #ef4444; background: #1b0f12; }
  .flow .step.end { border-color: #ef4444; background: #1b0f12; }
  .flow .num { font-weight: 700; color: #93c5fd; margin-right: 7px; }
  .flow .arrow { display: flex; align-items: center; color: #64748b; font-size: 18px; }
  details.ctx { background: #11203a; border: 1px solid #1e3a5f; border-radius: 10px; padding: 4px 14px; }
  details.ctx summary { cursor: pointer; font-weight: 700; font-size: 14px; color: #bfdbfe; padding: 8px 0; }
  details.ctx p { white-space: pre-wrap; font-size: 13.5px; line-height: 1.55; color: #cbd5e1; margin: 0 0 10px; }
  .wrap { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;
          max-width: 1500px; margin: 16px auto; padding: 0 20px; }
  @media (max-width: 1100px) { .wrap { grid-template-columns: 1fr; } }
  .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 18px; }
  .card h2 { margin: 0 0 12px; font-size: 15px; text-transform: uppercase;
             letter-spacing: .5px; color: #cbd5e1; }
  pre.sys { white-space: pre-wrap; background: #0b1220; border: 1px solid #334155;
            border-radius: 8px; padding: 12px; font-size: 12.5px; color: #cbd5e1; margin: 0; }
  .attacks { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }
  button { font: inherit; cursor: pointer; border-radius: 8px; border: 1px solid #475569;
           background: #334155; color: #e2e8f0; padding: 10px 12px; text-align: left; }
  button:hover { background: #3f4f6b; }
  button .tech { display: block; font-weight: 600; }
  button .desc { display: block; font-size: 12px; color: #94a3b8; margin-top: 2px; }
  textarea { width: 100%; min-height: 120px; border-radius: 8px; border: 1px solid #475569;
             background: #0b1220; color: #e2e8f0; padding: 10px; font: inherit; resize: vertical; }
  .row { display: flex; gap: 8px; margin-top: 8px; }
  .row button.primary { background: #2563eb; border-color: #2563eb; text-align: center; flex: 1; }
  .row button.ghost { background: transparent; }
  .verdict { display: inline-block; padding: 4px 12px; border-radius: 999px; font-weight: 700; font-size: 13px; }
  .verdict.bad { background: #7f1d1d; color: #fecaca; }
  .verdict.safe { background: #14532d; color: #bbf7d0; }
  .verdict.blocked { background: #1e3a8a; color: #bfdbfe; }
  .verdict.idle { background: #334155; color: #cbd5e1; }
  .usage { font-size: 12px; color: #94a3b8; margin-top: 8px; }
  .reply { white-space: pre-wrap; background: #0b1220; border: 1px solid #334155;
           border-radius: 8px; padding: 12px; margin-top: 12px; min-height: 60px; font-size: 14px; }
  mark { background: #f59e0b; color: #1f2937; padding: 0 3px; border-radius: 3px; font-weight: 700; }
  .muted { color: #94a3b8; font-size: 12px; }
  .label { font-size: 12px; color: #94a3b8; margin: 0 0 6px; }
  .trusted { background: #0b1f14; border: 1px solid #14532d; border-radius: 8px;
             padding: 10px 12px; margin: 0 0 12px; font-size: 13px; color: #bbf7d0; }
  .trusted .tag { display: inline-block; font-size: 11px; font-weight: 700;
             text-transform: uppercase; letter-spacing: .5px; color: #4ade80; margin-bottom: 4px; }
  .untag { display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase;
             letter-spacing: .5px; color: #f87171; margin-bottom: 4px; }
  .stage { border-left: 3px solid #475569; padding: 6px 0 6px 12px; margin: 0 0 10px; }
  .stage.hit { border-left-color: #ef4444; }
  .stage.safe { border-left-color: #22c55e; }
  .stage .sname { font-weight: 700; font-size: 13px; color: #e2e8f0; }
  .stage .stext { font-size: 13px; color: #cbd5e1; margin-top: 2px; }
  .why { background: #0b1220; border: 1px solid #334155; border-radius: 8px;
         padding: 12px; font-size: 13px; line-height: 1.5; color: #e2e8f0; margin-top: 12px; white-space: pre-wrap; }
  .why h3 { margin: 0 0 6px; font-size: 12px; text-transform: uppercase; letter-spacing: .5px; color: #f59e0b; }
  .why a { color: #93c5fd; }
  .tech-label { font-size: 13px; color: #93c5fd; margin: 0 0 12px; font-weight: 600; }
  .tools { margin: 12px 0 0; display: flex; flex-direction: column; gap: 6px; }
  .tool { display: flex; align-items: center; gap: 8px; font-size: 12.5px;
          background: #0b1220; border: 1px solid #334155; border-radius: 8px; padding: 7px 10px; }
  .tool .tname { font-weight: 700; font-family: ui-monospace, Menlo, monospace; }
  .tool .tdesc { color: #94a3b8; }
  .risk { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .4px;
          padding: 2px 7px; border-radius: 999px; white-space: nowrap; }
  .risk.safe { background: #14532d; color: #bbf7d0; }
  .risk.sensitive { background: #78350f; color: #fde68a; }
  .risk.dangerous { background: #7f1d1d; color: #fecaca; }
  .note { background: #0b1f2e; border: 1px solid #1e3a5f; border-radius: 8px; padding: 10px 12px;
          margin: 12px 0 0; font-size: 12px; color: #bfdbfe; }
  .note b { color: #93c5fd; }
  .toolcall { border-radius: 8px; padding: 12px; margin-top: 12px; border: 1px solid #334155; background: #0b1220; }
  .toolcall .tc-head { font-size: 11px; text-transform: uppercase; letter-spacing: .5px; color: #94a3b8; margin-bottom: 6px; }
  .toolcall .tc-call { font-family: ui-monospace, Menlo, monospace; font-size: 14px; font-weight: 700; word-break: break-all; }
  .toolcall .tc-status { margin-top: 8px; font-size: 12.5px; }
  .toolcall.executed-bad { border-color: #ef4444; background: #1b0f12; }
  .toolcall.executed-safe { border-color: #22c55e; background: #0c1f15; }
  .toolcall.blocked { border-color: #3b82f6; background: #0c1830; }
  .toolcall.held { border-color: #f59e0b; background: #1f1606; }
</style>
</head>
<body>
<header>
  <h1>Anatomy of an LLM Attack: hands-on labs</h1>
  <div class="controls">
    <label class="label" style="margin:0">Exercise:
      <select id="module"></select>
    </label>
    <span class="owasp" id="owasp"></span>
    <label class="switch" id="switch">
      <input type="checkbox" id="defense">
      <span>Defense layer (guardrails): <b id="defstate">OFF</b></span>
    </label>
    <details class="model">
      <summary>Model info</summary>
      <div class="grid" id="modelgrid"></div>
    </details>
  </div>
</header>

<p class="intro" id="intro"></p>

<section class="ctxwrap">
  <div class="flow" id="flow"></div>
  <details class="ctx" id="ctxBox" open>
    <summary>Scenario in detail: read this to understand the setup</summary>
    <p id="context"></p>
  </details>
</section>

<div class="wrap">
  <section class="card">
    <h2 id="leftTitle">Scenario</h2>
    <pre class="sys" id="sys"></pre>
    <div class="tools" id="tools"></div>
    <div class="note" id="note" style="display:none"></div>
    <p class="muted" style="margin-top:12px">Pick an attack, or write your own:</p>
    <div class="attacks" id="attacks"></div>
  </section>

  <section class="card">
    <h2 id="inputTitle">Send</h2>
    <div id="trustedBox" class="trusted" style="display:none">
      <span class="tag">Trusted: staff request (fixed)</span>
      <div id="trustedText"></div>
    </div>
    <p class="label" id="inputLabel"></p>
    <textarea id="msg"></textarea>
    <div class="row">
      <button class="primary" id="send">Send</button>
      <button class="ghost" id="clear">Clear</button>
    </div>
    <div style="margin-top:16px"><span class="verdict idle" id="verdict">No message sent yet</span></div>
    <div class="toolcall" id="toolcall" style="display:none"></div>
    <div class="usage" id="usage"></div>
    <div class="reply" id="reply"><span class="muted">The bot's reply will appear here.</span></div>
  </section>

  <section class="card">
    <h2>What just happened?</h2>
    <p class="tech-label" id="tech"></p>
    <div id="stages"><span class="muted">Send a message to see a stage-by-stage breakdown of the attack.</span></div>
    <div class="why" id="why" style="display:none"><h3>Why it works</h3><span id="whytext"></span></div>
  </section>
</div>

<footer style="max-width:1500px;margin:8px auto 28px;padding:0 20px;color:#64748b;font-size:12px;">
  Created by Razi Rais &middot; <a href="https://razibinrais.com" target="_blank" rel="noopener" style="color:#64748b">razibinrais.com</a> &middot; Licensed under MIT
</footer>

<script>
let current = null;          // current module info
let currentAttackId = null;
let highlights = [];

function esc(s){ return (s||'').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

function highlight(text){
  let html = esc(text);
  highlights.forEach(h => {
    if(!h) return;
    const pat = esc(h).replace(/[-]/g, '\\-?\\s*');
    html = html.replace(new RegExp(pat, 'ig'), m => '<mark>' + m + '</mark>');
  });
  return html;
}

async function loadModules(){
  const r = await fetch('/api/modules');
  const data = await r.json();
  const sel = document.getElementById('module');
  data.modules.forEach(m => {
    const o = document.createElement('option');
    o.value = m.id; o.textContent = m.title;
    sel.appendChild(o);
  });
  const g = document.getElementById('modelgrid');
  const mi = data.model;
  g.innerHTML =
    '<div class="k">Model</div><div>' + esc(mi.name) + '</div>' +
    '<div class="k">Parameters</div><div>' + esc(mi.parameter_size) + '</div>' +
    '<div class="k">Quantization</div><div>' + esc(mi.quantization) + '</div>' +
    '<div class="k">Family</div><div>' + esc(mi.family) + '</div>' +
    '<div class="k">Size on disk</div><div>' + (mi.size_mb ? mi.size_mb + ' MB' : 'unknown') + '</div>' +
    '<div class="k">Last request</div><div id="lastTokens">no request yet</div>';
  sel.onchange = () => loadModule(sel.value);
  await loadModule(data.modules[0].id);
}

async function loadModule(id){
  const r = await fetch('/api/module/' + id);
  current = await r.json();
  highlights = current.highlights || [];
  currentAttackId = null;
  document.getElementById('owasp').textContent = current.owasp;
  document.getElementById('intro').textContent = current.intro;
  document.getElementById('context').textContent = current.context || '';
  document.getElementById('ctxBox').style.display = current.context ? 'block' : 'none';
  const flowBox = document.getElementById('flow');
  flowBox.innerHTML = '';
  (current.flow || []).forEach((label, i, arr) => {
    const step = document.createElement('div');
    let cls = 'step';
    if(i === 0) cls += ' start';
    if(i === arr.length - 1) cls += ' end';
    step.className = cls;
    step.innerHTML = '<span class="num">' + (i + 1) + '</span>' + esc(label);
    flowBox.appendChild(step);
    if(i < arr.length - 1){
      const a = document.createElement('div');
      a.className = 'arrow';
      a.textContent = '\u2192';
      flowBox.appendChild(a);
    }
  });
  document.getElementById('leftTitle').textContent = current.scenario_title;
  document.getElementById('sys').textContent = current.scenario;
  const toolsBox = document.getElementById('tools');
  toolsBox.innerHTML = '';
  (current.tools || []).forEach(t => {
    const d = document.createElement('div');
    d.className = 'tool';
    d.innerHTML = '<span class="risk ' + esc(t.risk) + '">' + esc(t.risk) + '</span>' +
                  '<span class="tname">' + esc(t.name) + '(' + esc(t.args) + ')</span>' +
                  '<span class="tdesc">' + esc(t.description) + '</span>';
    toolsBox.appendChild(d);
  });
  const noteBox = document.getElementById('note');
  if(current.note){ noteBox.innerHTML = '<b>Note.</b> ' + esc(current.note); noteBox.style.display = 'block'; }
  else { noteBox.style.display = 'none'; }
  document.getElementById('inputTitle').textContent = current.input_title;
  const tbox = document.getElementById('trustedBox');
  if(current.trusted_instruction){
    document.getElementById('trustedText').textContent = current.trusted_instruction;
    tbox.style.display = 'block';
    document.getElementById('inputLabel').innerHTML = '<span class="untag">Untrusted: incoming data (the attack lands here)</span><br>' + esc(current.input_label);
  } else {
    tbox.style.display = 'none';
    document.getElementById('inputLabel').textContent = current.input_label;
  }
  document.getElementById('msg').placeholder = current.input_placeholder;
  const box = document.getElementById('attacks');
  box.innerHTML = '';
  current.attacks.forEach(a => {
    const b = document.createElement('button');
    b.innerHTML = '<span class="tech">' + esc(a.technique) + '</span>' +
                  '<span class="desc">' + esc(a.description) + '</span>';
    b.onclick = () => { document.getElementById('msg').value = a.payload; currentAttackId = a.id; send(); };
    box.appendChild(b);
  });
  resetOutput();
}

function resetOutput(){
  document.getElementById('reply').innerHTML = '<span class="muted">The bot\'s reply will appear here.</span>';
  const v = document.getElementById('verdict'); v.className = 'verdict idle'; v.textContent = 'No message sent yet';
  document.getElementById('usage').textContent = '';
  document.getElementById('toolcall').style.display = 'none';
  document.getElementById('tech').textContent = '';
  document.getElementById('stages').innerHTML = '<span class="muted">Send a message to see a stage-by-stage breakdown of the attack.</span>';
  document.getElementById('why').style.display = 'none';
}

function renderToolCall(tc){
  const box = document.getElementById('toolcall');
  if(!tc){ box.style.display = 'none'; return; }
  let cls = 'toolcall ';
  let statusText = '';
  if(tc.status === 'executed' && (tc.risk === 'dangerous' || tc.risk === 'sensitive')){
    cls += 'executed-bad'; statusText = 'EXECUTED (no policy stopped it)';
  } else if(tc.status === 'executed'){ cls += 'executed-safe'; statusText = 'EXECUTED (safe, read-only)'; }
  else if(tc.status === 'held'){ cls += 'held'; statusText = 'HELD for human approval'; }
  else { cls += 'blocked'; statusText = 'BLOCKED by policy'; }
  box.className = cls;
  box.innerHTML = '<div class="tc-head">Tool call ' +
                  '<span class="risk ' + esc(tc.risk) + '">' + esc(tc.risk) + '</span></div>' +
                  '<div class="tc-call">' + esc(tc.render) + '</div>' +
                  '<div class="tc-status"><b>' + esc(statusText) + '</b><br>' + esc(tc.reason || '') + '</div>';
  box.style.display = 'block';
}

function renderAnatomy(a){
  document.getElementById('tech').textContent = 'Technique: ' + a.technique;
  const stages = document.getElementById('stages');
  stages.innerHTML = '';
  a.stages.forEach((s, i) => {
    const d = document.createElement('div');
    let cls = 'stage';
    if(i === a.stages.length - 1){ cls += a.compromised ? ' hit' : ' safe'; }
    else if(i === 3 && a.blocked_by){ cls += ' safe'; }
    d.className = cls;
    d.innerHTML = '<div class="sname">' + esc(s.name) + '</div><div class="stext">' + esc(s.text) + '</div>';
    stages.appendChild(d);
  });
  const whyHtml = esc(a.why).replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
  document.getElementById('whytext').innerHTML = whyHtml;
  document.getElementById('why').style.display = 'block';
}

async function send(){
  if(!current) return;
  const msg = document.getElementById('msg').value.trim();
  if(!msg) return;
  const verdict = document.getElementById('verdict');
  const reply = document.getElementById('reply');
  verdict.className = 'verdict idle'; verdict.textContent = 'Asking the model...';
  reply.innerHTML = '<span class="muted">Thinking...</span>';
  try {
    const r = await fetch('/api/module/' + current.id + '/ask', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({message: msg, attack_id: currentAttackId, defended: document.getElementById('defense').checked})
    });
    const data = await r.json();
    reply.innerHTML = highlight(data.reply);
    renderToolCall(data.tool_call);
    if(data.compromised){ verdict.className = 'verdict bad'; verdict.textContent = current.success_label; }
    else if(data.blocked_by){
      let where = data.blocked_label;
      if(!where){ where = 'BLOCKED by ' + (data.blocked_by === 'input_guardrail' ? 'input guardrail' : (data.blocked_by === 'output_guardrail' ? 'output guardrail' : data.blocked_by)); }
      verdict.className = 'verdict blocked'; verdict.textContent = where;
    } else { verdict.className = 'verdict safe'; verdict.textContent = current.safe_label; }
    const u = data.usage || {};
    let tok;
    if(u.model && /router/i.test(u.model)){ tok = 'deterministic router (no model call, no tokens)'; }
    else if(u.input_tokens != null){ tok = 'input ' + u.input_tokens + ' tokens, output ' + (u.output_tokens != null ? u.output_tokens : '0') + ' tokens'; }
    else { tok = 'not reported (request was blocked before the model)'; }
    document.getElementById('usage').textContent = 'Tokens: ' + tok;
    const lt = document.getElementById('lastTokens'); if(lt) lt.textContent = tok;
    if(data.anatomy){ data.anatomy.compromised = data.compromised; renderAnatomy(data.anatomy); }
  } catch(e){
    verdict.className = 'verdict idle'; verdict.textContent = 'Error';
    reply.textContent = String(e);
  }
}

document.getElementById('send').onclick = () => { send(); };
document.getElementById('msg').addEventListener('input', () => { currentAttackId = null; });
document.getElementById('clear').onclick = () => { document.getElementById('msg').value = ''; currentAttackId = null; resetOutput(); };
document.getElementById('defense').addEventListener('change', (e) => {
  const on = e.target.checked;
  document.getElementById('defstate').textContent = on ? 'ON' : 'OFF';
  document.getElementById('switch').classList.toggle('on', on);
});
loadModules();
</script>
</body>
</html>
"""
