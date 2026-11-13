const $ = s => document.querySelector(s);
const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const api = (p, body, method) => fetch('/api' + p, body !== undefined || method ? {method: method || 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body || {})} : undefined).then(r => r.json());
const S = { id: null, mode: ['chat', 'research'].includes(localStorage.mode2) ? localStorage.mode2 : 'agent', busy: false, cur: null, tools: {} };
const ICONS = {bash: '›_', read_file: '📄', write_file: '✏️', list_dir: '📁', describe_image: '👁', web_search: '🔎', web_fetch: '🌐'};

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
const bottom = () => { const n = scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 140; if (n) scroller.scrollTop = scroller.scrollHeight; };
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
  const summ = name === 'bash' ? args.command : (args.path || args.query || args.url || '').split('/').pop();
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
function render(conv) {
  thread.innerHTML = ''; S.tools = {}; $('#title').textContent = conv.title;
  if (!conv.messages.length) return empty();
  const results = {}; conv.messages.forEach(m => { if (m.role === 'tool') results[m.tool_call_id] = m; });
  for (const m of conv.messages) {
    if (m.hidden) continue;
    if (m.role === 'user') {
      if (m.shell) { const p = botMsg(); toolCard(p, 'h' + Math.random(), 'bash', {command: m.shell.cmd}); const k = Object.keys(S.tools).pop(); toolDone(k, m.shell.code === 0, m.shell.output); }
      else userMsg(m.attachments ? (m.display || '') : (m.display || m.content), m.attachments);
    } else if (m.role === 'assistant') {
      const p = botMsg(); finishText(m.content || '', m.stats, p);
      for (const c of m.tool_calls || []) { const f = c.function, d = toolCard(p, c.id, f.name, f.arguments || {}); d.dataset.name = f.name; const r = results[c.id]; if (r) toolDone(c.id, r.ok !== false, r.content); }
      if (!p.children.length) p.remove();
    }
  }
  scroller.scrollTop = scroller.scrollHeight;
}

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
async function send(text) {
  text = (text ?? $('#input').value).trim();
  const atts = text.startsWith('!') ? [] : S.files.filter(f => f.state === 'ok');
  if ((!text && !atts.length) || S.busy) return;
  if (S.files.some(f => f.state === 'up')) { toast('Espera a que terminen de subir los archivos'); return; }
  if (!S.id) { const c = await api('/conversations', {}); S.id = c.id; }
  $('#input').value = ''; autosize();
  if (thread.querySelector('.empty')) thread.innerHTML = '';
  if (!text.startsWith('!')) userMsg(text, atts);
  S.files = S.files.filter(f => f.state === 'err' && false); drawTray();
  setBusy(true);
  let parent = botMsg(), raw = '', live = null, typing = el('div', 'typing', '<i></i><i></i><i></i>');
  parent.append(typing);
  const flush = (stats) => { if (live) { live.remove(); live = null; } finishText(raw, stats, parent); raw = ''; };
  try {
    const res = await fetch('/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({id: S.id, message: text, attachments: atts.map(f => ({name: f.name, path: f.path, kind: f.kind})), mode: S.mode, model: $('#modelSel').value, send_output: $('#sendOut').checked, auto_push: $('#autoPush').checked})});
    const rd = res.body.getReader(), dec = new TextDecoder(); let buf = '';
    while (true) {
      const {value, done} = await rd.read(); if (done) break;
      buf += dec.decode(value, {stream: true}); let i;
      while ((i = buf.indexOf('\n\n')) >= 0) {
        const line = buf.slice(0, i).replace(/^data: /, ''); buf = buf.slice(i + 2); if (!line) continue;
        const ev = JSON.parse(line); typing.remove();
        switch (ev.type) {
          case 'token': if (!live) { live = el('div', 'text'); parent.append(live); } raw += ev.text; live.textContent = raw; break;
          case 'clear_text': raw = ''; live?.remove(); live = null; break;
          case 'assistant_done': flush(ev.stats); break;
          case 'tool_start': { if (live) flush(); const d = toolCard(parent, ev.id, ev.name, ev.args); d.dataset.name = ev.name; break; }
          case 'tool_result': toolDone(ev.id, ev.ok, ev.output); parent = botMsg(); parent.append(typing); break;
          case 'approval': approval(ev.id, ev.name, ev.args); break;
          case 'notice': thread.append(el('div', 'notice', esc(ev.text))); break;
          case 'error': thread.append(el('div', 'notice err', esc(ev.text))); break;
          case 'title': $('#title').textContent = ev.title; loadConvs(); break;
          case 'git': toast(ev.pushed ? '✔ Subido a GitHub' : (ev.msg || 'Guardado localmente')); $('#ghMsg').textContent = ev.msg || ''; break;
        }
        bottom();
      }
    }
  } catch (e) { thread.append(el('div', 'notice err', 'Conexión perdida: ' + esc(e.message))); }
  typing.remove(); flush(); document.querySelectorAll('.msg.bot:empty').forEach(m => m.remove());
  setBusy(false); loadStatus(); loadConvs();
}

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
  if (sel.dataset.sig !== ms.join()) { sel.dataset.sig = ms.join(); const keep = localStorage.model || s.model; sel.innerHTML = ms.map(x => `<option>${esc(x)}</option>`).join(''); sel.value = ms.includes(keep) ? keep : (ms.includes(s.model) ? s.model : ms[0]); } $('#tpsTxt').textContent = s.tps ? s.tps + ' tokens/s' : '—'; $('#searchTxt').textContent = s.search ? 'Completa' : 'Limitada';
  const g = s.gpu; $('#dGpu').className = 'dot ' + (g ? 'ok' : 'bad');
  if (g) { $('#gpuName').textContent = g.name; $('#gpuUtil').textContent = g.util + ' %'; $('#vramBar').style.width = g.mem_used / g.mem_total * 100 + '%';
    $('#vramTxt').textContent = `${(g.mem_used / 1024).toFixed(1)} de ${(g.mem_total / 1024).toFixed(1)} GB`; $('#tempTxt').textContent = g.temp + ' °C'; }
  const t = s.git; $('#ghRepo').textContent = t.repo || 'sin remoto'; 
  $('#ghMeta').textContent = `rama ${t.branch} · ${t.workdir}` + (t.dirty ? ` · ${t.dirty} cambios sin subir` : '') + (t.ahead ? ` · ${t.ahead} commits pendientes` : '') + (t.token ? '' : ' · sin token');
}
async function loadConvs() {
  const l = await api('/conversations'), ul = $('#convs'); ul.innerHTML = '';
  for (const c of l) {
    const li = el('li', c.id === S.id ? 'on' : '', `<span>${esc(c.title)}</span>`), x = el('button', null, '✕'); x.title = 'Borrar';
    x.onclick = async e => { e.stopPropagation(); if (confirm('¿Borrar esta conversación?')) { await api('/conversations/' + c.id, {}, 'DELETE'); if (S.id === c.id) newConv(); else loadConvs(); } };
    li.onclick = async () => { S.id = c.id; render(await api('/conversations/' + c.id)); loadConvs(); $('#side').classList.remove('open'); };
    li.append(x); ul.append(li);
  }
}
function newConv() { S.id = null; $('#title').textContent = 'Nueva conversación'; empty(); loadConvs(); $('#side').classList.remove('open'); }

// ---------- eventos de UI
function autosize() { const i = $('#input'); i.style.height = 'auto'; i.style.height = Math.min(i.scrollHeight, 200) + 'px'; }
$('#input').addEventListener('input', autosize);
$('#input').addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });
$('#send').onclick = () => send();
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
