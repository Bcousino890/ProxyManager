const $ = s => document.querySelector(s);
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const api = (p, body, method) => fetch('/api' + p, body !== undefined || method ? {method: method || 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body || {})} : undefined).then(r => r.json());
const S = { id: null, mode: ['chat', 'research'].includes(localStorage.mode2) ? localStorage.mode2 : 'agent', busy: false, cur: null, tools: {} };
const ICONS = {edit_file: '🩹', search_files: '🔍', git_status: '🌿', git_diff: '±', git_commit: '✔', git_push: '⬆', run_tests: '🧪', proc_start: '▶', proc_inspect: '⚙', inspect_logs: '📜', plan: '🗂', project_init: '📦', memory_update: '🧠', bash: '›_', read_file: '📄', write_file: '✏️', list_dir: '📁', notify: '🔔', describe_image: '👁', web_search: '🔎', web_fetch: '🌐'};

function toast(t) { const x = $('#toast'); x.textContent = t; x.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => x.hidden = true, 3500); }
const fmtT = s => `${Math.floor(s / 3600)} h ${String(Math.floor(s % 3600 / 60)).padStart(2, '0')} min`;

// ---------- markdown mínimo
function md(src) {
  const blocks = []; 
  let t = src.replace(/```(\w*)\n?([\s\S]*?)(```|$)/g, (_, lang, code) => { blocks.push([lang, code.replace(/\n$/, '')]); return `\u0000${blocks.length - 1}\u0000`; });
  t = esc(t).replace(/`([^`\n]+)`/g, '<code>$1</code>').replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>')
    .replace(/^#{1,4} (.+)$/gm, '<b>$1</b>')
    .replace(/(?:^|\n)((?:[-*] .+(?:\n|$))+)/g, (_, l) => '<ul>' + l.trim().split('\n').map(x => '<li>' + x.replace(/^[-*] /, '') + '</li>').join('') + '</ul>')
    .replace(/(?:^|\n)((?:\d+\. .+(?:\n|$))+)/g, (_, l) => '<ol>' + l.trim().split('\n').map(x => '<li>' + x.replace(/^\d+\. /, '') + '</li>').join('') + '</ol>');
  t = t.split(/\n{2,}/).map(p => /^<(ul|ol)|\u0000\d+\u0000$/.test(p.trim()) ? p : '<p>' + p.replace(/\n/g, '<br>') + '</p>').join('');
  const root = el('div', 'text', t.replace(/\u0000(\d+)\u0000/g, '<span data-code="$1"></span>'));
  root.querySelectorAll('[data-code]').forEach(s => { s.replaceWith(codeBlock(...blocks[s.dataset.code])); });
  return root;
}
function codeBlock(lang, code) {
  const b = el('div', 'code'), h = el('div', 'code-h', `<span>${esc(lang || 'texto')}</span>`), bt = el('div', 'btns');
  const cp = el('button', null, 'Copiar'); cp.onclick = () => { navigator.clipboard.writeText(code); cp.textContent = '¡Copiado!'; setTimeout(() => cp.textContent = 'Copiar', 1200); };
  bt.append(cp);
  if (/^(bash|sh|shell|console)$/.test(lang)) { const r = el('button', null, 'Ejecutar en el pod'); r.onclick = () => send('!' + code); bt.append(r); }
  h.append(bt); b.append(h, el('pre', null, `<code>${esc(code)}</code>`)); return b;
}

// ---------- hilo
const thread = $('#thread'), scroller = $('#scroll');
S.stick = true;
const dist = () => scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight;
const bottom = (force) => { if (force) S.stick = true; if (S.stick) scroller.scrollTop = scroller.scrollHeight; };
scroller.addEventListener('scroll', () => { S.stick = dist() < 80; $('#jump').hidden = S.stick; }, {passive: true});
new ResizeObserver(() => { if (S.stick) scroller.scrollTop = scroller.scrollHeight; }).observe(thread);
$('#jump').onclick = () => { S.stick = true; scroller.scrollTo({top: scroller.scrollHeight, behavior: 'smooth'}); $('#jump').hidden = true; };
function empty() {
  thread.innerHTML = '';
  const e = el('div', 'empty', '<h2>¿Qué construimos hoy?</h2><div>El agente ejecuta comandos reales en el pod, edita archivos y sube todo a GitHub.</div>');
  const s = el('div', 'sugg');
  for (const t of ['Analiza el repositorio y dime qué falta por hacer', 'Crea un script en Python con pruebas que valide una lista de proxies', 'Muéstrame el estado de la GPU y de Ollama'])
    { const b = el('button', null, t); b.onclick = () => send(t); s.append(b); }
  e.append(s); thread.append(e);
}
function userMsg(t, atts) {
  const m = el('div', 'msg user');
  if (atts && atts.length) { const w = el('div', 'atts');
    for (const a of atts) w.append(a.kind === 'image' ? el('img', null, '') : el('span', 'f', '📄 ' + esc(a.name)));
    atts.forEach((a, i) => { if (a.kind === 'image') w.children[i].src = a.url || ('/api/file?path=' + encodeURIComponent(a.path)); });
    m.append(w); }
  if (t) m.append(document.createTextNode(t));
  thread.append(m); bottom(); }
function botMsg() { const m = el('div', 'msg bot'); thread.append(m); return m; }
function toolCard(parent, id, name, args) {
  const summ = name === 'bash' ? args.command : (args.command || args.path || args.query || args.url || args.pattern || args.message || args.name || args.action || '').toString().split('/').pop();
  const d = el('details', 'tool');
  d.innerHTML = `<summary><span class="ic">${ICONS[name] || '🔧'}</span><span class="nm">${esc(name)}</span><span class="arg">${esc(summ || '')}</span><span class="st run">ejecutando…</span></summary>`;
  if (name === 'write_file') d.append(el('pre', 'out', esc(args.content || '')));
  parent.append(d); S.tools[id] = d; bottom(); return d;
}
function toolDone(id, ok, out) {
  const d = S.tools[id]; if (!d) return;
  const st = d.querySelector('.st'); st.className = 'st ' + (ok ? 'ok' : 'bad'); st.textContent = ok ? 'listo' : 'falló';
  d.querySelector('.approve')?.remove();
  d.append(el('pre', 'out', esc(out))); if (!ok) d.open = true; bottom();
}
function approval(id, name, args) {
  const d = S.tools[id]; if (!d) return; d.open = true;
  const a = el('div', 'approve', '<span>⚠️ Comando potencialmente destructivo. ¿Ejecutar?</span>');
  const y = el('button', 'btn primary', 'Aprobar'), n = el('button', 'btn', 'Rechazar');
  y.onclick = () => { api('/approve', {id, ok: true}); a.remove(); }; n.onclick = () => { api('/approve', {id, ok: false}); a.remove(); };
  a.append(y, n); d.append(a); bottom();
}
function finishText(raw, stats, parent) {
  if (!raw.trim()) return null;
  const t = md(raw.replace(/<\/?tool_call>/g, '')); parent.append(t);
  if (stats && stats.tokens) parent.append(el('div', 'stats', `${stats.tokens} tokens${stats.tps ? ' · ' + stats.tps + ' tokens/s' : ''}`));
  return t;
}

// ---------- cargar conversación guardada
function render(conv, base) {
  thread.innerHTML = ''; S.tools = {}; $('#title').textContent = conv.title;
  if (base != null) conv = {...conv, messages: conv.messages.slice(0, base)};
  if (!conv.messages.length) return empty();
  const results = {}; conv.messages.forEach(m => { if (m.role === 'tool') results[m.tool_call_id] = m; });
  for (const m of conv.messages) {
    if (m.hidden) continue;
    if (m.role === 'user') {
      if (m.shell) { const p = botMsg(); toolCard(p, 'h' + Math.random(), 'bash', {command: m.shell.cmd}); const k = Object.keys(S.tools).pop(); toolDone(k, m.shell.code === 0, m.shell.output); }
      else userMsg(m.attachments ? (m.display || '') : (m.display || m.content), m.attachments);
    } else if (m.role === 'assistant') {
      const p = botMsg(); if (m.thinking) { const d = el('details', 'think', '<summary>💭 Razonamiento</summary>'); d.append(el('div', 'tt', esc(m.thinking))); p.append(d); }
      finishText(m.content || '', m.stats, p);
      for (const c of m.tool_calls || []) { const f = c.function, d = toolCard(p, c.id, f.name, f.arguments || {}); d.dataset.name = f.name; const r = results[c.id]; if (r) toolDone(c.id, r.ok !== false, r.content); }
      if (!p.children.length) p.remove();
    }
  }
  bottom(true); requestAnimationFrame(() => bottom(true));
}

// ---------- avisos
let beepCtx;
function beep() { try { beepCtx = beepCtx || new (window.AudioContext || window.webkitAudioContext)(); const o = beepCtx.createOscillator(), g = beepCtx.createGain();
  o.frequency.value = 880; g.gain.value = .08; o.connect(g); g.connect(beepCtx.destination); o.start(); g.gain.exponentialRampToValueAtTime(.0001, beepCtx.currentTime + .5); o.stop(beepCtx.currentTime + .5); } catch (_) {} }
const baseTitle = document.title;
window.addEventListener('focus', () => { document.title = baseTitle; });
function alertUser(title, text) {
  if (!$('#notifyOn').checked) return;
  beep(); toast('🔔 ' + (text || title).slice(0, 120));
  if (document.hidden) document.title = '✓ ' + title + ' — ' + baseTitle;
  try { if ('Notification' in window && Notification.permission === 'granted') new Notification(title, {body: (text || '').slice(0, 200)}); } catch (_) {}
}
$('#notifyOn').checked = localStorage.notifyOn !== '0';
$('#notifyOn').onchange = e => { localStorage.notifyOn = e.target.checked ? '1' : '0'; if (e.target.checked && 'Notification' in window && Notification.permission === 'default') Notification.requestPermission(); };
$('#think').checked = localStorage.think === '1';
$('#think').onchange = e => { localStorage.think = e.target.checked ? '1' : '0'; };

// ---------- adjuntos
S.files = [];
const fmtSz = n => n > 1048576 ? (n / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB';
function drawTray() {
  const t = $('#tray'); t.innerHTML = ''; t.hidden = !S.files.length;
  S.files.forEach((f, i) => {
    const c = el('div', 'chipf' + (f.state === 'up' ? ' up' : f.state === 'err' ? ' err' : ''));
    if (f.kind === 'image') c.append(el('img', null, '')), c.firstChild.src = f.url;
    c.append(el('div', null, `<div class="nm">${esc(f.name)}</div><div class="sz">${f.state === 'err' ? esc(f.msg) : f.state === 'up' ? 'subiendo…' : fmtSz(f.size)}</div>`));
    const x = el('button', null, '✕'); x.onclick = () => { S.files.splice(i, 1); drawTray(); }; c.append(x); t.append(c);
  });
}
async function addFiles(list) {
  for (const file of list) {
    const kind = /\.(png|jpe?g|webp|gif|bmp)$/i.test(file.name) || file.type.startsWith('image/') ? 'image' : 'file';
    const name = file.name && file.name !== 'image.png' ? file.name : `captura-${Date.now()}.png`;
    const f = {name, size: file.size, kind, state: 'up', url: kind === 'image' ? URL.createObjectURL(file) : null};
    S.files.push(f); drawTray();
    try {
      const r = await (await fetch('/api/upload?name=' + encodeURIComponent(name), {method: 'POST', body: file})).json();
      if (r.error) throw new Error(r.error);
      Object.assign(f, {path: r.path, kind: r.kind === 'image' ? 'image' : r.kind, state: 'ok'});
    } catch (e) { f.state = 'err'; f.msg = e.message; }
    drawTray();
  }
}
$('#attach').onclick = () => $('#fileInp').click();
$('#fileInp').onchange = e => { addFiles([...e.target.files]); e.target.value = ''; };
$('#input').addEventListener('paste', e => { const fs = [...(e.clipboardData?.files || [])]; if (fs.length) { e.preventDefault(); addFiles(fs); } });
['dragenter', 'dragover'].forEach(ev => document.addEventListener(ev, e => { if ([...(e.dataTransfer?.types || [])].includes('Files')) { e.preventDefault(); $('.composer').classList.add('drop'); } }));
['dragleave', 'drop'].forEach(ev => document.addEventListener(ev, e => { if (ev === 'drop' || e.target === document.documentElement || !e.relatedTarget) $('.composer').classList.remove('drop'); }));
document.addEventListener('drop', e => { if (e.dataTransfer?.files?.length) { e.preventDefault(); addFiles([...e.dataTransfer.files]); } });

// ---------- envío y streaming
function setBusy(b) { S.busy = b; $('#send').hidden = b; $('#stop').hidden = !b; $('#input').disabled = b; if (!b) $('#input').focus(); }
async function send(text, opts = {}) {
  text = (text ?? $('#input').value).trim();
  const atts = text.startsWith('!') || opts.attach ? [] : S.files.filter(f => f.state === 'ok');
  if ((!text && !atts.length && !opts.resume && !opts.attach) || S.busy) return;
  if (S.files.some(f => f.state === 'up')) { toast('Espera a que terminen de subir los archivos'); return; }
  if (!S.id) { const c = await api('/conversations', {}); S.id = c.id; }
  if (!opts.attach) { $('#input').value = ''; autosize(); }
  if (thread.querySelector('.empty')) thread.innerHTML = '';
  S.stick = true;
  S.files = S.files.filter(f => f.state === 'err' && false); drawTray();
  setBusy(true);
  let parent = botMsg(), raw = '', live = null, think = null, t0 = Date.now(), lastText = '', typing = el('div', 'typing', '<i></i><i></i><i></i>');
  parent.append(typing);
  const flush = (stats) => { if (live) { live.remove(); live = null; } if (raw.trim()) lastText = raw; finishText(raw, stats, parent); raw = ''; think = null; };
  try {
    const res = opts.attach ? await fetch('/api/runs/' + S.id + '?from=0') : await fetch(opts.resume ? '/api/resume' : '/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({id: S.id, think: $('#think').checked, message: text, attachments: atts.map(f => ({name: f.name, path: f.path, kind: f.kind})), mode: S.mode, model: $('#modelSel').value, send_output: $('#sendOut').checked, auto_push: $('#autoPush').checked, budget_min: +$('#budget').value || null})});
    const rd = res.body.getReader(), dec = new TextDecoder(); let buf = '';
    while (true) {
      const {value, done} = await rd.read(); if (done) break;
      buf += dec.decode(value, {stream: true}); let i;
      while ((i = buf.indexOf('\n\n')) >= 0) {
        const line = buf.slice(0, i).replace(/^data: /, ''); buf = buf.slice(i + 2); if (!line) continue;
        const ev = JSON.parse(line); typing.remove();
        switch (ev.type) {
          case 'thinking': { if (!think) { const d = el('details', 'think', '<summary>💭 Razonando…</summary>'); d.open = true; think = el('div', 'tt'); d.append(think); parent.insertBefore(d, typing.isConnected ? typing : null); }
            think.textContent += ev.text; think.scrollTop = think.scrollHeight; break; }
          case 'user': if (!ev.replay_skip) userMsg(ev.text, (ev.atts || []).map(x => ({...x, url: null}))); break;
          case 'status': paintAgent(ev); break;
          case 'plan': break;
          case 'outcome': if (ev.outcome !== 'done') toast({blocked: '⛔ Tarea BLOQUEADA', budget: '⏱ Presupuesto agotado', incomplete: '⚠ Tarea incompleta', error: '✖ Error', stopped: '■ Detenida'}[ev.outcome] || ev.outcome); break;
          case 'notify': alertUser(ev.title, ev.text); break;
          case 'token': if (!live) { live = el('div', 'text'); parent.append(live); } raw += ev.text; live.textContent = raw; break;
          case 'clear_text': raw = ''; live?.remove(); live = null; break;
          case 'assistant_done': flush(ev.stats); break;
          case 'tool_start': { if (live) flush(); const d = toolCard(parent, ev.id, ev.name, ev.args); d.dataset.name = ev.name; break; }
          case 'tool_result': toolDone(ev.id, ev.ok, ev.output); parent = botMsg(); parent.append(typing); break;
          case 'approval': approval(ev.id, ev.name, ev.args); break;
          case 'notice': thread.append(el('div', 'notice', esc(ev.text))); break;
          case 'error': thread.append(el('div', 'notice err', esc(ev.text))); break;
          case 'title': $('#title').textContent = ev.title; loadConvs(); break;
          case 'git': toast(ev.pushed ? '✔ Subido y verificado en GitHub' : (ev.msg || 'Guardado localmente')); $('#ghMsg').textContent = ev.msg || ''; break;
        }
        bottom();
      }
    }
  } catch (e) { thread.append(el('div', 'notice err', 'Conexión perdida: ' + esc(e.message))); }
  typing.remove(); flush(); document.querySelectorAll('.msg.bot:empty').forEach(m => m.remove());
  setBusy(false); loadStatus(); loadConvs();
  if (Date.now() - t0 > 8000 || document.hidden) alertUser('Tarea terminada', lastText.replace(/[#*`]/g, '').trim().split('\n')[0]);
}

// ---------- barra de estado del agente
const fmtM = s => s == null ? '∞' : `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
function paintAgent(s, status) {
  const bar = $('#agentbar'); if (!s || !s.phase) { bar.hidden = true; return; }
  bar.hidden = false;
  $('#abPhase').textContent = (status && status !== 'running' ? ({done: '✔ terminado', blocked: '⛔ BLOQUEADO', budget: '⏱ presupuesto agotado', incomplete: '⚠ incompleto', interrupted: '↻ interrumpido', error: '✖ error', stopped: '■ detenido'})[status] + ' · ' : '') + (s.phase || '');
  const cur = s.task || ''; $('#abTask').textContent = cur ? ' · ' + (cur.length > 60 ? cur.slice(0, 60) + '…' : cur) : '';
  const el_ = s.elapsed ?? s.elapsed_total; $('#abTime').textContent = `transcurrido ${fmtM(el_)}` + (s.remaining != null ? ` · restan ${fmtM(s.remaining)}` : '');
  const c = s.counts || {calls: s.calls, valid: s.valid, invalid: s.invalid, errors: s.errors}, n = c.calls || 0;
  const items = [['Llamadas', n], ['Válidas', n ? Math.round((n - (c.invalid || 0)) / n * 100) + ' %' : '—'], ['Errores', c.errors || 0], ['Archivos', s.n_files ?? (s.files || []).length],
    ['Pruebas', s.last_test ? (s.last_test.ok ? '✔ ' : '✖ ') + s.last_test.summary : '—'], ['Contexto', s.ctx ? Math.round(s.ctx / 327.68) + ' % (compact. ' + (s.compactions || 0) + ')' : '—'], ['Tokens/s', s.tps || '—'], ['Estancamiento', (s.strikes || 0) + '/4']];
  $('#abGrid').innerHTML = items.map(([k, v]) => `<div><span class="muted">${k}</span> <b>${esc(v)}</b></div>`).join('');
  const L = {pending: 'PENDIENTE', running: 'EJECUTANDO', done: 'COMPLETADO', failed: 'FALLIDO', blocked: 'BLOQUEADO'};
  $('#abTasks').innerHTML = (s.tasks || []).map((t, i) => `<li class="st-${L[t.status]}">${i + 1}. [${L[t.status]}] ${esc(t.text)}${t.evidence ? ` <span class="muted">— ${esc(t.evidence.slice(0, 80))}</span>` : ''}</li>`).join('');
  $('#abResume').hidden = !(['interrupted', 'blocked', 'incomplete', 'budget', 'stopped'].includes(status) && !S.busy);
}
$('#abResume').onclick = () => send('', {resume: true});

// ---------- estado y conversaciones
async function loadStatus() {
  let s; try { s = await api('/status'); } catch { return; }
  const c = s.clock; $('#clockTxt').textContent = fmtT(c.seconds); $('#clockCost').textContent = `≈ ${c.usd.toFixed(2).replace('.', ',')} USD`;
  $('#clockLimit').textContent = `límite ${c.limit_h} h`; $('#clockBar').style.width = Math.min(100, c.seconds / 3600 / c.limit_h * 100) + '%';
  $('#clockBar').style.background = c.seconds / 3600 > c.limit_h * .85 ? 'var(--bad)' : '';
  if (c.pod_id) $('#runpodLink').href = `https://www.runpod.io/console/pods?podId=${c.pod_id}`;
  const o = s.ollama; $('#dOllama').className = 'dot ' + (o.up ? 'ok' : 'bad'); $('#tOllama').textContent = o.up ? 'Responde' : 'Caído';
  $('#loadedTxt').textContent = o.loaded ? `${o.loaded.name} · ${o.loaded.gb} GB` : 'ninguno';
  const sel = $('#modelSel'), ms = o.models || [s.model];
  if (sel.dataset.sig !== ms.join()) { sel.dataset.sig = ms.join(); const keep = localStorage.model || s.model; sel.innerHTML = ms.map(x => `<option>${esc(x)}</option>`).join(''); sel.value = ms.includes(keep) ? keep : (ms.includes(s.model) ? s.model : ms[0]); } $('#tpsTxt').textContent = (s.ram ? `RAM ${(s.ram.used / 1024).toFixed(0)}/${(s.ram.total / 1024).toFixed(0)} GB · ` : '') + (s.num_ctx ? `ctx ${s.num_ctx / 1024}k · ` : '') + (s.tps ? s.tps + ' tokens/s' : '—'); $('#searchTxt').textContent = s.search ? 'Completa' : 'Limitada';
  const g = s.gpu; $('#dGpu').className = 'dot ' + (g ? 'ok' : 'bad');
  if (g) { $('#gpuName').textContent = g.name; $('#gpuUtil').textContent = g.util + ' %'; $('#vramBar').style.width = g.mem_used / g.mem_total * 100 + '%';
    $('#vramTxt').textContent = `${(g.mem_used / 1024).toFixed(1)} de ${(g.mem_total / 1024).toFixed(1)} GB`; $('#tempTxt').textContent = g.temp + ' °C'; }
  const t = s.git; $('#ghRepo').textContent = t.repo || 'sin remoto'; 
  $('#ghMeta').textContent = `rama ${t.branch}${t.branch !== t.target_branch ? ' (destino ' + t.target_branch + ')' : ''} @${t.head} · ${t.workdir} · ${({local: 'solo local', commit: 'commit local', push: 'subir rama'})[t.strategy]}` + (t.dirty ? ` · ${t.dirty} cambios sin subir` : '') + (t.ahead ? ` · ${t.ahead} commits pendientes` : '') + (t.token ? '' : ' · sin token');
}
const ago = ts => { const m = Math.floor((Date.now() / 1000 - ts) / 60); return m < 1 ? 'ahora' : m < 60 ? `hace ${m} min` : m < 1440 ? `hace ${Math.floor(m / 60)} h` : new Date(ts * 1000).toLocaleDateString('es', {day: 'numeric', month: 'short'}); };
const grpOf = ts => { const d0 = new Date(); d0.setHours(0, 0, 0, 0); const day = (d0.getTime() / 1000 - ts) / 86400;
  return ts >= d0.getTime() / 1000 ? 'Hoy' : day <= 1 ? 'Ayer' : day <= 7 ? 'Últimos 7 días' : 'Anteriores'; };
async function loadConvs() {
  const all = await api('/conversations'), q = $('#convq').value.trim().toLowerCase(), ul = $('#convs'); ul.innerHTML = '';
  const l = all.filter(c => (c.n > 0 || c.id === S.id) && (!q || c.title.toLowerCase().includes(q)));
  if (!l.length) ul.append(el('li', 'grp', q ? 'Sin resultados' : 'Aún no hay conversaciones'));
  let last = '';
  for (const c of l) {
    const g = grpOf(c.updated); if (g !== last) { ul.append(el('li', 'grp', g)); last = g; }
    const li = el('li', c.id === S.id ? 'on' : '', `<span class="t" title="${esc(c.title)}">${esc(c.title)}</span><span class="when">${({interrupted: '↻ interrumpida · ', blocked: '⛔ bloqueada · ', running: '▶ en curso · '})[c.state] || ''}${ago(c.updated)}</span>`), x = el('button', null, '✕'); x.title = 'Borrar';
    x.onclick = async e => { e.stopPropagation(); if (confirm('¿Borrar esta conversación?')) { await api('/conversations/' + c.id, {}, 'DELETE'); if (S.id === c.id) newConv(); else loadConvs(); } };
    li.onclick = async () => { if (S.busy) { toast('Hay una tarea en curso en la vista actual'); return; } S.id = c.id; const conv = await api('/conversations/' + c.id), r = await api('/run/' + c.id);
      if (r.active) { render(conv, r.base); send('', {attach: true}); } else { render(conv); paintAgent(r.run ? {...r.run, ...(r.run.status === 'interrupted' || r.run.status === 'blocked' || r.run.status === 'incomplete' ? {resumable: true} : {})} : null, r.run && r.run.status); }
      loadConvs(); $('#side').classList.remove('open'); };
    li.append(x); ul.append(li);
  }
}
$('#convq').addEventListener('input', () => loadConvs());
function newConv() { S.id = null; $('#title').textContent = 'Nueva conversación'; empty(); loadConvs(); $('#side').classList.remove('open'); }

// ---------- eventos de UI
function autosize() { const i = $('#input'); i.style.height = 'auto'; i.style.height = Math.min(i.scrollHeight, 200) + 'px'; }
$('#input').addEventListener('input', autosize);
$('#input').addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });
$('#send').onclick = () => { if ($('#notifyOn').checked && 'Notification' in window && Notification.permission === 'default') Notification.requestPermission(); send(); };
$('#stop').onclick = () => api('/stop', {id: S.id});
$('#newConv').onclick = newConv;
$('#openSide').onclick = () => $('#side').classList.add('open'); $('#closeSide').onclick = () => $('#side').classList.remove('open');
$('#resetClock').onclick = async () => { await api('/clock/reset', {}); loadStatus(); };
$('#btnPush').onclick = async () => { $('#btnPush').disabled = true; const r = await api('/git/push', {}); $('#ghMsg').textContent = r.msg || (r.pushed ? 'Subido.' : r.committed ? 'Commit local.' : 'Nada que subir.'); toast(r.pushed ? '✔ Subido a GitHub' : (r.msg || 'Sin cambios')); $('#btnPush').disabled = false; loadStatus(); };
$('#btnPull').onclick = async () => { const r = await api('/git/pull', {}); $('#ghMsg').textContent = r.msg || ''; toast(r.ok ? '✔ Traído de GitHub' : 'Error al traer'); loadStatus(); };
$('#btnToken').onclick = () => $('#tokenDlg').showModal();
$('#tokenSave').onclick = async () => { await api('/git/token', {token: $('#tokenInp').value}); $('#tokenInp').value = ''; toast('Token guardado en el pod'); loadStatus(); };
$('#btnSearchKey').onclick = () => $('#searchDlg').showModal();
$('#searchSave').onclick = async () => { await api('/search/key', {key: $('#searchInp').value}); $('#searchInp').value = ''; toast('Clave de búsqueda guardada'); loadStatus(); };
document.querySelectorAll('#modeSeg button').forEach(b => { b.onclick = () => { S.mode = b.dataset.mode; localStorage.mode2 = S.mode; paintMode(); }; });
function paintMode() { document.querySelectorAll('#modeSeg button').forEach(b => b.classList.toggle('on', b.dataset.mode === S.mode)); $('#autoPush').disabled = S.mode === 'chat';
  $('#input').placeholder = {chat: 'MODO CHAT: el modelo solo conversa, NO ejecuta nada. Cambia a Agente para que actúe.',
    research: 'Describe qué investigar. El agente buscará, leerá varias fuentes y escribirá un informe con citas en pod-work/investigaciones…',
    agent: 'Dile al agente qué hacer…  ·  !comando se ejecuta en el pod  ·  /leer URL'}[S.mode];
  $('.composer').style.borderColor = S.mode === 'chat' ? 'var(--warn)' : ''; }
$('#modelSel').onchange = e => { localStorage.model = e.target.value; };
paintMode(); empty(); loadStatus(); loadConvs(); setInterval(loadStatus, 8000);

// ---------- configuración de GitHub
$('#btnGhCfg').onclick = async () => { const s = await api('/status'), g = s.git; $('#cfgRepo').value = g.repo; $('#cfgBranch').value = g.target_branch; $('#cfgDir').value = g.workdir; $('#cfgStrat').value = g.strategy; $('#cfgMsg').textContent = ''; $('#ghDlg').showModal(); };
$('#cfgSave').onclick = async () => { const r = await api('/config', {repo: $('#cfgRepo').value, branch: $('#cfgBranch').value, workdir: $('#cfgDir').value, strategy: $('#cfgStrat').value}); $('#cfgMsg').textContent = r.ok ? 'Guardado.' : r.msg; if (r.ok) loadStatus(); };
$('#cfgVerify').onclick = async () => { const r = await api('/git/verify'); $('#cfgMsg').textContent = r.remote == null ? 'No pude consultar GitHub: ' + r.msg : r.remote === '' ? `La rama ${r.branch} aún no existe en GitHub (local ${r.local.slice(0, 10)})` : `local ${r.local.slice(0, 10)} · remoto ${r.remote.slice(0, 10)} → ${r.match ? '✔ coinciden' : '✖ DIFIEREN'}`; };
$('#cfgIntegrate').onclick = async () => { const t = prompt('Rama de destino (debe existir en GitHub, p. ej. main). Solo avance rápido, sin force:', 'main'); if (!t) return; if (!confirm(`¿Integrar la rama de trabajo en «${t}»?`)) return; const r = await api('/git/integrate', {target: t}); $('#cfgMsg').textContent = r.msg; };
