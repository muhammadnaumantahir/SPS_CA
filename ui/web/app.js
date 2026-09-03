const $ = (id) => document.getElementById(id);
const EXT = {python:'py',javascript:'js',typescript:'ts',java:'java',go:'go',csharp:'cs'};
const STORAGE_KEY = 'sps-ca-chat-session';

const defaultLayers = [
  ['Software DNA Layer','Constraints and meta-rules.'],
  ['Governance Layer','Decision gates and risk assessment.'],
  ['Cognitive Layer','Reasoning and planning — Brain interface.'],
  ['Knowledge Layer','Structured domain knowledge.'],
  ['Experience Layer','Historical memory and feedback.'],
  ['Meta-Learning Layer','Strategy improvement.'],
  ['Adaptation Layer','Context-aware behavior adjustment.'],
  ['Evolution Layer','Capability creation from failure patterns.'],
  ['Verification & Validation Layer','Sandboxed testing.'],
  ['Execution Layer','Applies validated changes.']
];

let session = loadSession();
let lastTurnData = null;

function esc(value = '') {
  return String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

// === VIEW SWITCHING ===
function switchView(view) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const el = $(`view-${view}`);
  if (el) el.classList.add('active');
  const btn = document.querySelector(`.nav-btn[data-view="${view}"]`);
  if (btn) btn.classList.add('active');
  if (view === 'structure') loadStructureView();
  if (view === 'capabilities') loadCapabilitiesView();
  if (view === 'growth') loadGrowthView();
}

// === STRUCTURE VIEW (live architecture manifest) ===
let structureLoaded = false;
async function loadStructureView() {
  const pipeline = $('structurePipeline');
  if (!pipeline) return;
  if (structureLoaded) return;
  try {
    const resp = await fetch('/api/architecture');
    const data = await resp.json();
    const layers = data.layers || [];

    pipeline.innerHTML = layers.map((l, idx) => `
      <div class="structure-node">
        <button class="structure-head" onclick="this.parentElement.classList.toggle('expanded')">
          <span class="sn-num">L${String(l.number).padStart(2, '0')}</span>
          <span class="sn-name">${esc(l.name)}</span>
          <span class="sn-caret">▾</span>
        </button>
        <div class="structure-body">
          <p>${esc(l.purpose || l.description || '')}</p>
          ${(l.sub_components || []).length ? `<div class="sn-subs">${l.sub_components.map(s => `<span class="sn-sub">${esc(s)}</span>`).join('')}</div>` : ''}
        </div>
      </div>
      ${idx < layers.length - 1 ? '<div class="structure-arrow">↓</div>' : ''}
    `).join('');

    const brain = data.brain || {};
    $('structureBrainBody').innerHTML = `
      <div class="info-row"><small>ROLE</small><strong>${esc(brain.role || '')}</strong></div>
      <div class="info-row"><small>DEFAULT PROVIDER</small><strong>${esc(brain.default_provider || 'Ollama')}</strong></div>
      <div class="info-row"><small>REPLACEABLE</small><strong>${brain.replaceable ? 'Yes — swap via models/' : 'No'}</strong></div>
      <div class="info-row"><small>BOUNDARY</small><strong>${esc(brain.boundary || '')}</strong></div>
    `;

    const subsystems = data.supporting_subsystems || [];
    $('structureSubsystemsBody').innerHTML = subsystems.map(s => `<span class="lang-chip">${esc(s)}</span>`).join('') || '<span class="muted-text">None listed.</span>';

    structureLoaded = true;
  } catch (e) {
    pipeline.innerHTML = '<div class="muted-text">Failed to load architecture.</div>';
  }
}

// === MINI PIPELINE ===
function renderMiniPipeline(layers) {
  const el = $('miniPipeline');
  if (!el) return;
  el.innerHTML = (layers || defaultLayers.map((x,i) => ({number:i+1,name:x[0],status:'ready'}))).map(l =>
    `<div class="mini-layer"><span class="ml-num">L${String(l.number).padStart(2,'0')}</span><span>${esc(l.name)}</span><span class="ml-status">${esc(l.status||'ready')}</span></div>`
  ).join('');
}

// === MARKDOWN-LITE RENDERING (fenced code blocks, like a normal chatbot) ===
let codeBlockCounter = 0;

function renderCodeBlock(lang, code) {
  const id = `codeblock-${++codeBlockCounter}`;
  return `<div class="code-block">
    <div class="code-block-head">
      <span class="code-block-lang">${esc(lang || 'code')}</span>
      <button type="button" class="code-copy-btn" onclick="copyCodeBlock('${id}', this)">Copy</button>
    </div>
    <pre><code id="${id}">${esc(code)}</code></pre>
  </div>`;
}

function renderInlineText(text) {
  if (!text || !text.trim()) return '';
  const withInlineCode = esc(text).replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  const paragraphs = withInlineCode.trim().split(/\n{2,}/).map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`);
  return paragraphs.join('');
}

function renderMarkdown(content) {
  if (!content) return '';
  const parts = String(content).split(/```([a-zA-Z0-9_+-]*)\n([\s\S]*?)```/g);
  let html = '';
  for (let i = 0; i < parts.length; i++) {
    if (i % 3 === 0) {
      html += renderInlineText(parts[i]);
    } else {
      html += renderCodeBlock(parts[i], parts[i + 1] || '');
      i += 1;
    }
  }
  return html;
}

function copyCodeBlock(id, btn) {
  const el = document.getElementById(id);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent).then(() => {
    const original = btn.textContent;
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = original; btn.classList.remove('copied'); }, 1500);
  });
}

function toggleDetail(id) {
  const el = $(id);
  if (el) el.classList.toggle('hidden');
}

// === MESSAGES ===
function renderMessages() {
  const messages = $('messages');
  if (!session.conversation.length) {
    messages.innerHTML = `<div class="welcome-msg"><div class="welcome-icon">✦</div><div><strong>Hello — I'm SPS-CA.</strong><p>Attach code, describe the task, and keep talking — I'll reply with explanation and code together, right here in the chat. Every response has Agree/Disagree — disagree to trigger capability evolution.</p></div></div>`;
    return;
  }
  let html = '';
  session.conversation.forEach((msg, idx) => {
    const isUser = msg.role === 'user';
    html += `<div class="message-row ${isUser ? 'user-message' : 'assistant-message'}">
      <div class="message-avatar">${isUser ? 'U' : 'S'}</div>
      <div class="message-content">
        <div class="message-role">${isUser ? 'You' : 'SPS-CA'}</div>
        <div class="message-bubble">${isUser ? `<p>${esc(msg.content).replace(/\n/g, '<br>')}</p>` : renderMarkdown(msg.content)}</div>
      </div>
    </div>`;
    // Add feedback + diff/trace toggles after assistant messages from this session
    if (!isUser && msg.content && msg.turnData) {
      const tid = msg.turnId || idx;
      const hasDiff = msg.turnData.diff && msg.turnData.diff.trim();
      html += `<div class="feedback-row" id="feedback-${tid}">
        <button class="feedback-btn agree" onclick="sendFeedback(${tid}, 'agree')" id="agree-${tid}">👍 Agree</button>
        <button class="feedback-btn disagree" onclick="sendFeedback(${tid}, 'disagree')" id="disagree-${tid}">👎 Disagree — create capability</button>
        ${hasDiff ? `<button class="feedback-btn detail-toggle" onclick="toggleDetail('diff-${tid}')">🔍 Diff</button>` : ''}
        <button class="feedback-btn detail-toggle" onclick="toggleDetail('trace-${tid}')">🧬 Trace</button>
      </div>
      ${hasDiff ? `<pre class="detail-block hidden" id="diff-${tid}">${esc(msg.turnData.diff)}</pre>` : ''}
      <pre class="detail-block hidden" id="trace-${tid}">${esc(JSON.stringify(msg.turnData, null, 2))}</pre>`;
    }
  });
  messages.innerHTML = html;
  messages.scrollTop = messages.scrollHeight;
}

// === FEEDBACK (AGREE / DISAGREE) ===
async function sendFeedback(turnId, type) {
  const agreeBtn = $(`agree-${turnId}`);
  const disagreeBtn = $(`disagree-${turnId}`);
  if (agreeBtn) agreeBtn.disabled = true;
  if (disagreeBtn) disagreeBtn.disabled = true;

  try {
    const response = await fetch('/api/feedback', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        turn_id: turnId,
        feedback: type,
        request: lastTurnData?.intent || '',
        code: $('code').value,
        language: session.language,
        capability_id: lastTurnData?.capability_results?.slice(-1)?.[0]?.capability_id || '',
      }),
    });
    const data = await response.json();

    if (type === 'disagree' && data.evolution) {
      // Show evolution notification
      const fb = $(`feedback-${turnId}`);
      if (fb) {
        const note = document.createElement('div');
        note.className = 'muted-text';
        note.style.cssText = 'margin-top:6px;font-size:11px;';
        note.textContent = data.evolution.capability_id
          ? `🔄 Evolution triggered — new capability ${data.evolution.capability_id} is being analyzed.`
          : `🔄 Disagreement recorded. Pattern will trigger evolution after repeated failures.`;
        fb.appendChild(note);
      }
      if (agreeBtn) agreeBtn.style.display = 'none';
      if (disagreeBtn) { disagreeBtn.classList.add('sent'); disagreeBtn.textContent = '👎 Disagreed'; }
    } else {
      if (agreeBtn) { agreeBtn.classList.add('sent'); agreeBtn.textContent = '👍 Agreed'; }
      if (disagreeBtn) disagreeBtn.style.display = 'none';
    }
  } catch (e) {
    console.error('Feedback error:', e);
    if (agreeBtn) agreeBtn.disabled = false;
    if (disagreeBtn) disagreeBtn.disabled = false;
  }
}

// === CAPABILITIES VIEW ===
let capsCache = [];
let capsFilter = 'all';

function capMatchesFilter(cap, filter) {
  if (filter === 'all') return true;
  if (filter === 'usable') return !!cap.usable;
  if (filter === 'deprecated') return !cap.usable;
  if (filter === 'seed') return !cap.generated;
  if (filter === 'generated') return !!cap.generated;
  return true;
}

function renderCapsGrid() {
  const grid = $('capsGrid');
  if (!grid) return;
  const caps = capsCache.filter(c => capMatchesFilter(c, capsFilter));
  if (!caps.length) {
    grid.innerHTML = '<div class="muted-text">No capabilities match this filter.</div>';
    return;
  }
  grid.innerHTML = caps.map(cap => `
    <div class="cap-card ${cap.generated ? 'generated' : 'seed'} ${cap.usable ? '' : 'cap-deprecated'}">
      <div class="cap-card-top">
        <div class="cap-id">${esc(cap.id)}</div>
        <span class="cap-usable-badge ${cap.usable ? 'usable' : 'unusable'}">${cap.usable ? '● Usable' : '○ ' + esc(cap.status || 'inactive')}</span>
      </div>
      <h3>${esc(cap.name)}</h3>
      <p>${esc(cap.description)}</p>
      <div class="cap-meta">
        <div><span>Version</span> <strong>${esc(cap.version)}</strong></div>
        <div><span>Origin</span> <strong>${cap.generated ? 'Generated' : 'Seed'}</strong></div>
        <div><span>Reused</span> <strong>${cap.reuse_count ?? 0}×</strong></div>
        <div><span>Test coverage</span> <strong>${Math.round((cap.test_coverage || 0) * 100)}%</strong></div>
      </div>
      <div class="cap-langs">${(cap.supported_languages && cap.supported_languages.length ? cap.supported_languages : (cap.tags || [])).map(l => `<span class="lang-chip sm">${esc(l)}</span>`).join('') || '<span class="muted-text">all languages</span>'}</div>
      ${cap.failure_pattern ? `<div class="cap-failure-pattern"><small>Grown from</small> ${esc(cap.failure_pattern)}</div>` : ''}
    </div>
  `).join('');
}

async function loadCapabilitiesView() {
  const grid = $('capsGrid');
  if (!grid) return;
  grid.innerHTML = '<div class="muted-text">Loading capabilities…</div>';
  try {
    const resp = await fetch('/api/capabilities');
    const data = await resp.json();
    capsCache = data.capabilities || [];
    renderCapsGrid();
  } catch (e) {
    grid.innerHTML = '<div class="muted-text">Failed to load capabilities.</div>';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const filterBar = $('capsFilter');
  if (filterBar) {
    filterBar.addEventListener('click', (e) => {
      const btn = e.target.closest('.chip-filter');
      if (!btn) return;
      filterBar.querySelectorAll('.chip-filter').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      capsFilter = btn.dataset.filter;
      renderCapsGrid();
    });
  }
});

// === GROWTH VIEW ===
function renderGrowthChart(series) {
  const el = $('growthChart');
  if (!el) return;
  if (!series || series.length < 2) {
    el.innerHTML = '<div class="muted-text">Not enough history yet — disagree with a result to start tracking growth.</div>';
    return;
  }
  const values = series.map(p => p.capabilities);
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const w = 640, h = 160, pad = 24;
  const range = Math.max(max - min, 1);
  const stepX = (w - pad * 2) / (series.length - 1);
  const points = values.map((v, i) => {
    const x = pad + i * stepX;
    const y = h - pad - ((v - min) / range) * (h - pad * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  const line = points.join(' ');
  const area = `${pad},${h - pad} ${line} ${w - pad},${h - pad}`;
  const dots = values.map((v, i) => {
    const [x, y] = points[i].split(',');
    return `<circle cx="${x}" cy="${y}" r="3.5" class="growth-dot"></circle>`;
  }).join('');
  el.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}" class="growth-svg" preserveAspectRatio="none">
      <polygon points="${area}" class="growth-area"></polygon>
      <polyline points="${line}" class="growth-line"></polyline>
      ${dots}
    </svg>
    <div class="growth-chart-labels"><span>start</span><span>now — ${values[values.length - 1]} capabilities</span></div>
  `;
}

async function loadGrowthView() {
  const stats = $('growthStats');
  const timeline = $('growthTimeline');
  if (!stats || !timeline) return;

  try {
    const resp = await fetch('/api/growth');
    const data = await resp.json();

    stats.innerHTML = `
      <div class="stat-card"><div class="stat-value">${data.total_capabilities || 0}</div><div class="stat-label">Total Capabilities</div></div>
      <div class="stat-card"><div class="stat-value">${data.usable_capabilities ?? data.total_capabilities ?? 0}</div><div class="stat-label">Usable Now</div></div>
      <div class="stat-card"><div class="stat-value">${data.seed_capabilities || 0}</div><div class="stat-label">Seed Capabilities</div></div>
      <div class="stat-card"><div class="stat-value">${data.generated_capabilities || 0}</div><div class="stat-label">Generated Capabilities</div></div>
      <div class="stat-card"><div class="stat-value">${data.total_disagreements || 0}</div><div class="stat-label">User Disagreements</div></div>
      <div class="stat-card"><div class="stat-value">${data.total_agreements || 0}</div><div class="stat-label">User Agreements</div></div>
      <div class="stat-card"><div class="stat-value">${data.total_tasks || 0}</div><div class="stat-label">Total Tasks</div></div>
      <div class="stat-card"><div class="stat-value">${data.success_rate || '—'}</div><div class="stat-label">Success Rate</div></div>
    `;

    renderGrowthChart(data.growth_series);

    if (data.timeline && data.timeline.length) {
      timeline.innerHTML = data.timeline.map(entry => `
        <div style="padding:12px;border:1px solid var(--line);border-radius:10px;margin-bottom:10px;background:var(--panel3);">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <strong style="font-size:13px;">${esc(entry.event || 'Task')}</strong>
            <span style="font-size:10px;color:var(--muted);">${esc(entry.timestamp || '')}</span>
          </div>
          <p style="margin:4px 0 0;font-size:11px;color:var(--muted);">${esc(entry.description || '')}</p>
        </div>
      `).join('');
    } else {
      timeline.innerHTML = '<div class="timeline-empty">No evolution events yet. Use the chat and disagree with results to trigger capability growth.</div>';
    }
  } catch (e) {
    stats.innerHTML = '<div class="muted-text">Failed to load growth data.</div>';
    timeline.innerHTML = '';
  }
}

// === SESSION ===
const STORAGE_KEY_HISTORY = 'sps-ca-chat-history';
const MAX_HISTORY = 30;

function loadSession() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    return {
      conversation: Array.isArray(saved.conversation) ? saved.conversation : [],
      code: typeof saved.code === 'string' ? saved.code : 'def add(a, b):\n    return a + b\n',
      language: saved.language || 'python',
      filename: saved.filename || 'main.py',
      turns: Number(saved.turns || 0),
    };
  } catch { return {conversation:[], code:'def add(a, b):\n    return a + b\n', language:'python', filename:'main.py', turns:0}; }
}
function saveSession() { localStorage.setItem(STORAGE_KEY, JSON.stringify(session)); }
function syncSessionMeta() {
  $('turnCount').textContent = `Turn ${session.turns}`;
  $('sessionTurns').textContent = String(session.turns);
  $('sessionLanguage').textContent = session.language;
  $('sessionFile').textContent = session.filename;
}

// === CHAT HISTORY (backups of past chats, kept in localStorage) ===
function loadHistory() {
  try {
    const list = JSON.parse(localStorage.getItem(STORAGE_KEY_HISTORY) || '[]');
    return Array.isArray(list) ? list : [];
  } catch { return []; }
}
function saveHistory(list) {
  localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(list.slice(0, MAX_HISTORY)));
}
function sessionTitle(sess) {
  const firstUser = sess.conversation.find(m => m.role === 'user');
  if (!firstUser || !firstUser.content) return 'Untitled chat';
  const text = firstUser.content.trim().replace(/\s+/g, ' ');
  return text.length > 48 ? text.slice(0, 48) + '…' : text;
}
function backupCurrentSession() {
  if (!session.conversation.length) return; // nothing to back up
  const history = loadHistory();
  history.unshift({
    id: `chat-${Date.now()}`,
    title: sessionTitle(session),
    timestamp: new Date().toISOString(),
    turns: session.turns,
    language: session.language,
    session: JSON.parse(JSON.stringify(session)),
  });
  saveHistory(history);
}
function renderHistoryPanel() {
  const panel = $('historyPanel');
  if (!panel) return;
  const history = loadHistory();
  if (!history.length) {
    panel.innerHTML = '<div class="muted-text history-empty">No backed-up chats yet. Starting a new chat backs up the current one here.</div>';
    return;
  }
  panel.innerHTML = history.map(h => `
    <div class="history-item">
      <div class="history-item-main" onclick="restoreSession('${h.id}')">
        <div class="history-item-title">${esc(h.title)}</div>
        <div class="history-item-meta">${esc(h.language)} · ${h.turns} turn${h.turns === 1 ? '' : 's'} · ${new Date(h.timestamp).toLocaleString()}</div>
      </div>
      <button class="history-delete" onclick="deleteHistoryItem(event, '${h.id}')" title="Delete backup">✕</button>
    </div>
  `).join('');
}
function toggleHistoryPanel() {
  const panel = $('historyPanel');
  panel.classList.toggle('hidden');
  if (!panel.classList.contains('hidden')) renderHistoryPanel();
}
function restoreSession(id) {
  const history = loadHistory();
  const entry = history.find(h => h.id === id);
  if (!entry) return;
  backupCurrentSession(); // don't lose whatever's currently open
  session = entry.session;
  saveSession();
  $('language').value = session.language;
  $('code').value = session.code;
  renderMessages();
  syncSessionMeta();
  $('historyPanel').classList.add('hidden');
}
function deleteHistoryItem(event, id) {
  event.stopPropagation();
  saveHistory(loadHistory().filter(h => h.id !== id));
  renderHistoryPanel();
}

// === SEND MESSAGE ===
async function sendMessage(event) {
  event?.preventDefault();
  const request = $('request').value.trim();
  const code = $('code').value;
  if (!request || !code || $('runBtn').disabled) return;

  session.language = $('language').value;
  session.filename = `main.${EXT[session.language] || 'txt'}`;
  session.code = code;
  $('runBtn').disabled = true;
  $('runBtn').innerHTML = 'Thinking… <span class="spinner"></span>';
  $('pipelineState').textContent = 'Reasoning';

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        request, code, language: session.language,
        filename: session.filename, model: $('model').value,
        conversation: session.conversation,
      }),
    });
    const data = await response.json();
    if (!response.ok && !data.assistant_message) throw new Error(data.error || 'Request failed');

    const turnId = session.turns;
    const assistantMsg = data.assistant_message || data.error || 'No response.';

    session.conversation = Array.isArray(data.conversation)
      ? data.conversation.map((m, i) => {
          // Mark the last assistant message with turnData for feedback buttons
          if (m.role === 'assistant' && i === data.conversation.length - 1) {
            return {...m, turnData: data, turnId: turnId};
          }
          return m;
        })
      : [
          ...session.conversation,
          {role:'user', content:request},
          {role:'assistant', content:assistantMsg, turnData:data, turnId:turnId},
        ];

    lastTurnData = data;
    session.code = data.output_code || code;
    session.turns += 1;
    $('code').value = session.code;
    $('request').value = '';
    saveSession();
    renderMessages();
    syncSessionMeta();
    applyTurn(data);
  } catch (error) {
    $('pipelineState').textContent = 'Failed';
    $('reasoning').innerHTML = `<span class="error-text">${esc(error.message)}</span>`;
  } finally {
    $('runBtn').disabled = false;
    $('runBtn').innerHTML = 'Send <span>&#x2197;</span>';
  }
}

// === APPLY TURN RESULTS ===
function applyTurn(data) {
  $('pipelineState').textContent = data.success ? 'Complete' : 'Needs attention';
  const layers = data.layers || defaultLayers.map((x,i) => ({number:i+1,name:x[0],status:'ready'}));
  renderMiniPipeline(layers);
  $('brainProvider').textContent = data.brain?.provider || 'Ollama';
  $('providerText').textContent = data.brain?.provider || 'Ollama';
  $('modelText').textContent = data.brain?.model || $('model').value;
  $('reasoning').innerHTML = `<b>Intent</b><p>${esc(data.intent)}</p><b>Reasoning</b><p>${esc(data.reasoning || 'The Brain produced the plan.')}</p>`;
}

// === NEW CHAT ===
function newChat() {
  backupCurrentSession();
  session = {conversation:[], code:$('code').value, language:$('language').value, filename:`main.${EXT[$('language').value]||'txt'}`, turns:0};
  localStorage.removeItem(STORAGE_KEY);
  lastTurnData = null;
  renderMessages();
  syncSessionMeta();
  $('request').value = '';
  $('pipelineState').textContent = 'Ready';
  $('reasoning').innerHTML = '<span class="muted-text">Waiting for your first request…</span>';
  renderMiniPipeline();
}

// === LOAD SAMPLE ===
function loadSample() {
  const code = `def divide(a, b):\n    return a / b\n`;
  $('code').value = code;
  $('request').value = 'Add input validation to this function so division by zero is handled safely.';
  session.code = code;
  session.language = 'python';
  session.filename = 'main.py';
  saveSession();
  syncSessionMeta();
}

// === EVENT LISTENERS ===
$('chatForm').addEventListener('submit', sendMessage);
$('newChatBtn').addEventListener('click', newChat);
$('historyBtn').addEventListener('click', toggleHistoryPanel);
$('sampleBtn').addEventListener('click', loadSample);
$('collapseCodeBtn').addEventListener('click', () => {
  $('codeDock').classList.toggle('collapsed');
  $('collapseCodeBtn').textContent = $('codeDock').classList.contains('collapsed') ? 'Open' : 'Close';
});
$('attachCodeBtn').addEventListener('click', () => {
  $('codeDock').classList.remove('collapsed');
  $('collapseCodeBtn').textContent = 'Close';
  $('codeDock').scrollIntoView({behavior:'smooth', block:'center'});
});
$('language').addEventListener('change', () => {
  session.language = $('language').value;
  session.filename = `main.${EXT[session.language]||'txt'}`;
  syncSessionMeta(); saveSession();
});
$('model').addEventListener('input', () => $('modelText').textContent = $('model').value);
$('code').addEventListener('input', () => { session.code = $('code').value; saveSession(); });

// === INIT ===
(function init() {
  $('language').value = session.language;
  $('code').value = session.code;
  $('modelText').textContent = $('model').value;
  renderMessages();
  syncSessionMeta();
  renderMiniPipeline();
})();
