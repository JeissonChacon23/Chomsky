"""Interfaz web (HTML + CSS + JS en un solo texto para que Vercel siempre lo empaquete)."""

INDEX_HTML = r'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GLC → Forma Normal de Chomsky</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#f2f4f8;--panel:#fff;--ink:#14213d;--muted:#5b6579;--line:#d7dce6;--accent:#0f6b63;--accent-ink:#fff;
--del:#b42318;--del-bg:#fdecea;--add:#067647;--add-bg:#e6f6ee;--code:#f6f8fb}
@media (prefers-color-scheme:dark){:root{--bg:#0e1422;--panel:#161e30;--ink:#e8ecf5;--muted:#9aa5bd;--line:#2a3550;
--accent:#3cc3b4;--accent-ink:#06201d;--del:#ff8a80;--del-bg:#3a1b1d;--add:#6fdba0;--add-bg:#12301f;--code:#0f1626}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 "IBM Plex Sans",system-ui,sans-serif}
header{padding:28px 24px 8px;max-width:1280px;margin:auto}
h1{font-size:1.6rem;margin:0 0 4px;letter-spacing:-.01em}
header p{margin:0;color:var(--muted);max-width:70ch}
main{display:grid;grid-template-columns:minmax(300px,380px) 1fr;gap:20px;max-width:1280px;margin:auto;padding:16px 24px 48px}
@media (max-width:900px){main{grid-template-columns:1fr}}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px}
aside .panel{position:sticky;top:12px}
label{display:block;font-weight:500;margin:12px 0 4px}
label small{font-weight:400;color:var(--muted)}
input,textarea{width:100%;padding:9px 10px;border:1px solid var(--line);border-radius:6px;background:var(--code);color:var(--ink);
font:14px/1.5 "IBM Plex Mono",ui-monospace,monospace}
textarea{min-height:130px;resize:vertical}
input:focus,textarea:focus,button:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.actions{display:grid;gap:8px;margin-top:16px}
.actions h2{font-size:.95rem;margin:10px 0 0;color:var(--muted);font-weight:500}
button{font:500 14px "IBM Plex Sans",sans-serif;padding:9px 12px;border-radius:6px;border:1px solid var(--line);background:var(--panel);
color:var(--ink);cursor:pointer;text-align:left}
button:hover:not(:disabled){border-color:var(--accent)}
button:disabled{opacity:.45;cursor:not-allowed}
button.primary{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
button.quiet{border-style:dashed}
.errors{background:var(--del-bg);color:var(--del);border-radius:8px;padding:12px 16px;margin-bottom:14px}
.errors ul{margin:6px 0 0;padding-left:20px}
.okmsg{background:var(--add-bg);color:var(--add);border-radius:8px;padding:10px 14px;margin-bottom:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px;margin-bottom:14px}
.card h3{margin:0 0 2px;font-size:1.1rem}
.card .desc{color:var(--muted);margin:0 0 12px;max-width:75ch}
.card.final{border:2px solid var(--accent)}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:700px){.pair{grid-template-columns:1fr}}
.box h4{margin:0 0 4px;font-size:.9rem;font-weight:600}
pre{margin:0;padding:10px 12px;background:var(--code);border-radius:6px;overflow-x:auto;font:14px/1.6 "IBM Plex Mono",monospace}
.ident{margin:12px 0 0;display:grid;gap:8px}
.ident div{display:flex;flex-wrap:wrap;gap:6px;align-items:baseline}
.ident b{font-weight:600;margin-right:4px}
.chip{background:var(--code);border:1px solid var(--line);border-radius:5px;padding:1px 8px;font:13px "IBM Plex Mono",monospace}
.diff{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
@media (max-width:700px){.diff{grid-template-columns:1fr}}
.del,.add{border-radius:6px;padding:8px 12px}
.del{background:var(--del-bg);color:var(--del)}.add{background:var(--add-bg);color:var(--add)}
.del h4,.add h4{margin:0 0 4px;font-size:.9rem}
.del code,.add code{display:block;font:14px/1.6 "IBM Plex Mono",monospace}
.note{margin:10px 0 0;padding:8px 12px;border-left:3px solid var(--accent);background:var(--code);border-radius:0 6px 6px 0;font-size:.93rem}
.empty{color:var(--muted);text-align:center;padding:48px 16px}
.badge{display:inline-block;padding:1px 10px;border-radius:99px;font-size:.85rem;font-weight:600}
.badge.ok{background:var(--add-bg);color:var(--add)}.badge.error{background:var(--del-bg);color:var(--del)}
.tip{font-size:.85rem;color:var(--muted);margin:6px 0 0}
</style>
</head>
<body>
<header>
  <h1>De gramática libre de contexto a Forma Normal de Chomsky</h1>
  <p>Ingrese una gramática, valídela y vea cada transformación con la gramática antes y después, las producciones eliminadas y las agregadas.</p>
</header>
<main>
<aside>
  <div class="panel">
    <label for="variables">Variables <small>(separadas por coma o espacio)</small></label>
    <input id="variables" autocomplete="off" placeholder="S, A, B">
    <div class="row">
      <div><label for="terminals">Terminales</label><input id="terminals" autocomplete="off" placeholder="a, b"></div>
      <div><label for="start">Símbolo inicial</label><input id="start" autocomplete="off" placeholder="S"></div>
    </div>
    <label for="productions">Producciones <small>(una línea por variable, alternativas con |)</small></label>
    <textarea id="productions" spellcheck="false" placeholder="S -> A S B | ε"></textarea>
    <p class="tip">La cadena vacía se escribe ε (también λ, epsilon o &amp;). Los nombres pueden tener varios caracteres, como X1.</p>
    <div class="actions">
      <button class="primary" id="btn-validate">Validar gramática</button>
      <button class="quiet" id="btn-example">Cargar gramática de ejemplo</button>
      <h2>Paso a paso</h2>
      <button class="step" data-step="nulas" disabled>Eliminar producciones nulas</button>
      <button class="step" data-step="unitarias" disabled>Eliminar producciones unitarias</button>
      <button class="step" data-step="inutiles" disabled>Eliminar variables inútiles</button>
      <button class="step" data-step="inalcanzables" disabled>Eliminar variables inalcanzables</button>
      <button class="step" data-step="fnc" disabled>Convertir a Forma Normal de Chomsky</button>
      <h2>Automático</h2>
      <button class="primary step" id="btn-all" disabled>Ejecutar proceso completo</button>
      <button id="btn-reset">Ingresar nueva gramática</button>
    </div>
  </div>
</aside>
<section id="results" aria-live="polite"></section>
</main>
<script>
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let original = null, current = null, history = [], isCnf = false, errors = [];

async function api(url, body) {
  const res = await fetch(url, body ? {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)} : {});
  return res.json();
}
const form = () => ({variables:$('variables').value, terminals:$('terminals').value, start:$('start').value, productions:$('productions').value});
const setButtons = on => document.querySelectorAll('.step').forEach(b => b.disabled = !on);

async function loadExample() {
  const e = await api('/api/example');
  $('variables').value = e.variables; $('terminals').value = e.terminals;
  $('start').value = e.start; $('productions').value = e.productions;
}

async function validateGrammar() {
  const res = await api('/api/validate', form());
  history = []; isCnf = false;
  if (!res.ok) { original = current = null; errors = res.errors; setButtons(false); render(); return; }
  errors = []; original = current = res.grammar; setButtons(true); render();
}

async function runStep(key) {
  if (!current) return;
  const res = await api('/api/step', {grammar: current, step: key});
  if (!res.ok) { errors = res.errors; render(); return; }
  errors = []; history.push(...res.steps); current = res.grammar; isCnf = res.is_cnf; render(true);
}

async function runAll() {
  if (!original) return;
  const res = await api('/api/run', {grammar: original});
  if (!res.ok) { errors = res.errors; render(); return; }
  errors = []; history = res.steps; current = res.grammar; isCnf = res.is_cnf; render(true);
}

function resetAll() {
  ['variables','terminals','start','productions'].forEach(id => $(id).value = '');
  original = current = null; history = []; isCnf = false; errors = []; setButtons(false); render();
}

const chips = items => items.map(i => `<span class="chip">${esc(i)}</span>`).join('');
const lines = list => list.map(esc).join('\n');

function stepCard(s, n) {
  const badge = s.status ? ` <span class="badge ${s.status}">${s.status === 'ok' ? 'Válida' : 'No válida'}</span>` : '';
  const ident = s.identified.map(i => `<div><b>${esc(i.label)}:</b>${chips(i.items)}</div>`).join('');
  const del = s.removed.length ? `<div class="del"><h4>Producciones eliminadas</h4>${s.removed.map(p => `<code>− ${esc(p)}</code>`).join('')}</div>` : '';
  const add = s.added.length ? `<div class="add"><h4>Producciones agregadas</h4>${s.added.map(p => `<code>+ ${esc(p)}</code>`).join('')}</div>` : '';
  const vars = [s.variables_removed.length ? `Variables eliminadas: ${s.variables_removed.join(', ')}` : '',
                s.variables_added.length ? `Variables nuevas: ${s.variables_added.join(', ')}` : ''].filter(Boolean)
                .map(t => `<p class="note">${esc(t)}</p>`).join('');
  const notes = s.notes.map(t => `<p class="note">${esc(t)}</p>`).join('');
  const diff = (del || add) ? `<div class="diff">${del}${add}</div>` : '';
  return `<article class="card" id="step-${n}"><h3>Paso ${n}. ${esc(s.title)}${badge}</h3><p class="desc">${esc(s.description)}</p>
    <div class="pair"><div class="box"><h4>Gramática inicial de la etapa</h4><pre>${lines(s.before.lines)}</pre></div>
    <div class="box"><h4>Gramática resultante</h4><pre>${lines(s.after.lines)}</pre></div></div>
    <div class="ident">${ident}</div>${diff}${vars}${notes}</article>`;
}

function grammarHeader(g) {
  return `V = {${g.variables.join(', ')}}\nT = {${g.terminals.join(', ')}}\nS = ${g.start}\n\n`;
}

function render(scroll) {
  let html = '';
  if (errors.length) html += `<div class="errors"><strong>La gramática tiene errores. Corríjalos para iniciar la conversión.</strong><ul>${errors.map(e => `<li>${esc(e)}</li>`).join('')}</ul></div>`;
  if (original) {
    html += `<div class="okmsg">Gramática válida. Ya puede ejecutar las etapas.</div>`;
    html += `<article class="card"><h3>Gramática original</h3><pre>${esc(grammarHeader(original))}${lines(original.lines)}</pre></article>`;
  }
  history.forEach((s, i) => html += stepCard(s, i + 1));
  if (original && isCnf) {
    html += `<article class="card final" id="final"><h3>Gramática final en Forma Normal de Chomsky <span class="badge ok">Válida</span></h3>
      <pre>${esc(grammarHeader(current))}${lines(current.lines)}</pre></article>`;
  }
  if (!html) html = `<div class="card empty">Escriba una gramática o cargue el ejemplo, y luego pulse «Validar gramática».</div>`;
  $('results').innerHTML = html;
  if (scroll) { const el = $('final') || $('step-' + history.length); if (el) el.scrollIntoView({behavior:'smooth', block:'start'}); }
}

$('btn-validate').onclick = validateGrammar;
$('btn-example').onclick = async () => { await loadExample(); await validateGrammar(); };
$('btn-reset').onclick = resetAll;
$('btn-all').onclick = runAll;
document.querySelectorAll('button[data-step]').forEach(b => b.onclick = () => runStep(b.dataset.step));
render();
</script>
</body>
</html>
'''
