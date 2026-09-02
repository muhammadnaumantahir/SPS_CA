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
  if (view === 'capabilities') loadCapabilitiesView();
  if (view === 'growth') loadGrowthView();
}

// === MINI PIPELINE ===
function renderMiniPipeline(layers) {
  const el = $('miniPipeline');
  if (!el) return;
  el.innerHTML = (layers || defaultLayers.map((x,i) => ({number:i+1,name:x[0],status:'ready'}))).map(l =>
    `<div class="mini-layer"><span class="ml-num">L${String(l.number).padStart(2,'0')}</span><span>${esc(l.name)}</span><span class="ml-status">${esc(l.status||'ready')}</span></div>`
  ).join('');
}

// === MESSAGES ===
function renderMessages() {
  const messages = $('messages');
  if (!session.conversation.length) {
    messages.innerHTML = `<div class="welcome-msg"><div class="welcome-icon">✦</div><div><strong>Hello — I'm SPS-CA.</strong><p>Paste code, describe the task, and keep talking. Every response has Agree/Disagree — disagree to trigger capability evolution.</p></div></div>`;
    return;
  }
  let html = '';
  session.conversation.forEach((msg, idx) => {
    const isUser = msg.role === 'user';
    html += `<div class="message-row ${isUser ? 'user-message' : 'assistant-message'}">
      <div class="message-avatar">${isUser ? 'U' : 'S'}</div>
      <div class="message-content">
        <div class="message-role">${isUser ? 'You' : 'SPS-CA'}</div>
        <div class="message-bubble">${esc(msg.content)}</div>
      </div>
    </div>`;
    // Add feedback buttons after assistant messages
    if (!isUser && msg.content && msg.turnData) {
      const tid = msg.turnId || idx;
      html += `<div class="feedback-row" id="feedback-${tid}">
        <button class="feedback-btn agree" onclick="sendFeedback(${tid}, 'agree')" id="agree-${tid}">👍 Agree</button>
        <button class="feedback-btn disagree" onclick="sendFeedback(${tid}, 'disagree')" id="disagree-${tid}">👎 Disagree — create capability</button>
      </div>`;
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
async function loadCapabilitiesView() {
  const grid = $('capsGrid');
  if (!grid) return;
  grid.innerHTML = '<div class="muted-text">Loading capabilities…</div>';
  try {
    const resp = await fetch('/api/capabilities');
    const data = await resp.json();
    const caps = data.capabilities || [];
    grid.innerHTML = caps.map(cap => `
      <div class="cap-card ${cap.generated ? 'generated' : 'seed'}">
        <div class="cap-id">${esc(cap.id)}</div>
        <h3>${esc(cap.name)}</h3>
        <p>${esc(cap.description)}</p>
        <div class="cap-meta">
          <div><span>Version</span> <strong>${esc(cap.version)}</strong></div>
          <div><span>Type</span> <strong>${cap.generated ? 'Generated' : 'Seed'}</strong></div>
          <div><span>Languages</span> <strong>${(cap.tags || []).join(', ') || 'all'}</strong></div>
        </div>
      </div>
    `).join('');
  } catch (e) {
    grid.innerHTML = '<div class="muted-text">Failed to load capabilities.</div>';
  }
}

// === GROWTH VIEW ===
async function loadGrowthView() {
  const stats = $('growthStats');
  const timeline = $('growthTimeline');
  if (!stats || !timeline) return;

  try {
    const resp = await fetch('/api/growth');
    const data = await resp.json();

    stats.innerHTML = `
      <div class="stat-card"><div class="stat-value">${data.total_capabilities || 0}</div><div class="stat-label">Total Capabilities</div></div>
      <div class="stat-card"><div class="stat-value">${data.seed_capabilities || 0}</div><div class="stat-label">Seed Capabilities</div></div>
      <div class="stat-card"><div class="stat-value">${data.generated_capabilities || 0}</div><div class="stat-label">Generated Capabilities</div></div>
      <div class="stat-card"><div class="stat-value">${data.total_disagreements || 0}</div><div class="stat-label">User Disagreements</div></div>
      <div class="stat-card"><div class="stat-value">${data.total_tasks || 0}</div><div class="stat-label">Total Tasks</div></div>
      <div class="stat-card"><div class="stat-value">${data.success_rate || '—'}</div><div class="stat-label">Success Rate</div></div>
    `;

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
  $('output').textContent = data.output_code || session.code || 'No code.';
  $('diff').textContent = data.diff || 'No changes.';
  $('trace').textContent = JSON.stringify(data, null, 2);
}

// === NEW CHAT ===
function newChat() {
  session = {conversation:[], code:$('code').value, language:$('language').value, filename:`main.${EXT[$('language').value]||'txt'}`, turns:0};
  localStorage.removeItem(STORAGE_KEY);
  lastTurnData = null;
  renderMessages();
  syncSessionMeta();
  $('request').value = '';
  $('pipelineState').textContent = 'Ready';
  $('reasoning').innerHTML = '<span class="muted-text">Waiting for your first request…</span>';
  $('output').textContent = session.code;
  $('diff').textContent = 'No diff yet.';
  $('trace').textContent = 'No trace yet.';
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

// === TAB SWITCHING ===
document.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  ['output','diff','trace'].forEach(id => $(id).classList.toggle('hidden', id !== btn.dataset.tab));
}));

// === EVENT LISTENERS ===
$('chatForm').addEventListener('submit', sendMessage);
$('newChatBtn').addEventListener('click', newChat);
$('sampleBtn').addEventListener('click', loadSample);
$('collapseCodeBtn').addEventListener('click', () => {
  $('codeDock').classList.toggle('collapsed');
  $('collapseCodeBtn').textContent = $('codeDock').classList.contains('collapsed') ? 'Expand' : 'Collapse';
});
$('attachCodeBtn').addEventListener('click', () => $('codeDock').scrollIntoView({behavior:'smooth', block:'center'}));
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
