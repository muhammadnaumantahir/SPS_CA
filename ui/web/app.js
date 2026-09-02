const $ = (id) => document.getElementById(id);
const EXT = {python:'py',javascript:'js',typescript:'ts',java:'java',go:'go',csharp:'cs'};
const STORAGE_KEY = 'sps-ca-chat-session';

const defaultLayers = [
  ['Software DNA layer','Absolute source of truth: constraints and meta-rules.'],
  ['Governance layer','Authorizes proposed changes against Software DNA.'],
  ['Cognitive core','Synthesizes goals and system state into decisions and plans.'],
  ['Knowledge core','Manages structured, evolving domain knowledge.'],
  ['Experience core','Stores feedback and runtime signals as historical memory.'],
  ['Meta-learning core','Evaluates and improves the system’s learning process.'],
  ['Adaptation core','Changes strategy by context without modifying source code.'],
  ['Evolution core','Drives structural self-growth and capability creation.'],
  ['Verification & Validation','Tests, simulates and validates proposed changes.'],
  ['Execution layer','Applies validated decisions through controlled actions.']
];

let session = loadSession();

function esc(value = '') {
  return String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function chips(items = []) {
  return items.map((item) => `<span class="sub-chip">${esc(item)}</span>`).join('');
}

function renderPipeline(layers = defaultLayers.map((x, i) => ({
  number:i + 1, name:x[0], purpose:x[1], description:x[1], sub_components:[], status:'ready'
}))) {
  $('pipeline').innerHTML = layers.map((layer) => `
    <article class="layer" data-layer="${layer.number}">
      <div class="layer-top">
        <div class="layer-num">L${String(layer.number).padStart(2,'0')}</div>
        <div class="layer-status">${esc(layer.status || 'ready')}</div>
      </div>
      <div class="layer-body">
        <strong>${esc(layer.name)}</strong>
        <small>${esc(layer.purpose || layer.description || '')}</small>
        ${layer.sub_components?.length ? `<div class="subcomponents"><span class="sub-label">SUB-COMPONENTS</span><div class="sub-chip-list">${chips(layer.sub_components)}</div></div>` : ''}
      </div>
    </article>`).join('');
}

function setLayers(statusMap = {}) {
  document.querySelectorAll('.layer').forEach((el) => {
    const n = el.dataset.layer;
    if (statusMap[n]) el.querySelector('.layer-status').textContent = statusMap[n];
  });
}

function loadSession() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    return {
      conversation: Array.isArray(saved.conversation) ? saved.conversation : [],
      code: typeof saved.code === 'string' ? saved.code : $('code')?.value || '',
      language: saved.language || 'python',
      filename: saved.filename || 'main.py',
      turns: Number(saved.turns || 0),
    };
  } catch {
    return {conversation:[], code:'', language:'python', filename:'main.py', turns:0};
  }
}

function saveSession() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

function syncSessionMeta() {
  $('turnCount').textContent = `Turn ${session.turns}`;
  $('sessionTurns').textContent = String(session.turns);
  $('sessionLanguage').textContent = session.language;
  $('sessionFile').textContent = session.filename;
}

function renderMessages() {
  const messages = $('messages');
  if (!session.conversation.length) {
    messages.innerHTML = `<div class="welcome-message"><div class="welcome-icon">✦</div><div><strong>Hello — I’m SPS-CA.</strong><p>Paste code, describe the task, and keep talking. Follow-up feedback is applied to the current working code and recent conversation.</p></div></div>`;
    return;
  }
  messages.innerHTML = session.conversation.map((message) => {
    const isUser = message.role === 'user';
    return `<div class="message-row ${isUser ? 'user-message' : 'assistant-message'}">
      <div class="message-avatar">${isUser ? 'U' : 'S'}</div>
      <div class="message-content"><div class="message-role">${isUser ? 'You' : 'SPS-CA'}</div><div class="message-bubble">${esc(message.content)}</div></div>
    </div>`;
  }).join('');
  messages.scrollTop = messages.scrollHeight;
}

async function loadArchitecture() {
  try {
    const data = await fetch('/api/architecture').then((response) => response.json());
    renderPipeline(data.layers);
    $('brainProvider').textContent = data.brain.default_provider;
    $('providerText').textContent = data.brain.default_provider;
    $('architecture').innerHTML = `
      <div class="brain-node"><span>🧠</span><div><strong>${esc(data.brain.name)}</strong><small>${esc(data.brain.role)}</small></div><b>SEPARATE</b></div>
      <div class="boundary-arrow">↓</div>
      <div class="architecture-note"><strong>10-Layer SPS-CA Architecture</strong><span>Sub-components are modular and optional.</span></div>
      <div class="layer-map">${data.layers.map((layer) => `
        <details class="map-layer"><summary><span>L${String(layer.number).padStart(2,'0')}</span><strong>${esc(layer.name)}</strong><em>${layer.sub_components?.length || 0} components</em></summary>
          <p>${esc(layer.purpose || layer.description || '')}</p>
          <div class="sub-chip-list">${chips(layer.sub_components || [])}</div>
        </details>`).join('')}</div>
      <div class="supporting"><b>Supporting subsystems</b>${(data.supporting_subsystems || []).map((x) => `<span>${esc(x)}</span>`).join('')}</div>`;
  } catch {
    renderPipeline();
  }
}

function renderCapabilityResults(items = []) {
  $('capabilities').innerHTML = items.length ? items.map((item, i) => `
    <div class="cap-item"><span>${String(i + 1).padStart(2,'0')}</span><div><strong>${esc(item.name || item.capability_id || item.id)}</strong><small>${esc(item.reason || item.summary || 'Selected by Brain')}</small></div><b>${esc(item.status || 'planned')}</b></div>`).join('') : '<div class="empty">No capability was required for this turn.</div>';
}

function applyTurn(data) {
  $('pipelineState').textContent = data.success ? 'Complete' : 'Needs attention';
  const status = {};
  (data.layers || []).forEach((layer) => { status[layer.number] = layer.status; });
  setLayers(status);
  $('brainProvider').textContent = data.brain?.provider || 'Ollama';
  $('providerText').textContent = data.brain?.provider || 'Ollama';
  $('modelText').textContent = data.brain?.model || $('model').value;
  $('reasoning').innerHTML = `<b>Intent</b><p>${esc(data.intent)}</p><b>Reasoning</b><p>${esc(data.reasoning || 'The Brain produced the plan for this turn.')}</p>`;
  $('decision').innerHTML = `<div class="intent">${esc(data.intent || 'No explicit intent returned')}</div><div class="decision-note">The Brain reasoned over this turn and the prior conversation. Capabilities remain separate executable SPS skills.</div>`;
  renderCapabilityResults(data.capability_results || []);
  $('output').textContent = data.output_code || session.code || 'No current code.';
  $('diff').textContent = data.diff || 'No changes in this turn.';
  $('trace').textContent = JSON.stringify(data, null, 2);
}

async function sendMessage(event) {
  event?.preventDefault();
  const request = $('request').value.trim();
  const code = $('code').value;
  if (!request || !code || $('runBtn').disabled) return;

  session.language = $('language').value;
  session.filename = `main.${EXT[session.language] || 'txt'}`;
  session.code = code;
  $('runBtn').disabled = true;
  $('runBtn').innerHTML = 'SPS-CA is thinking… <span class="spinner"></span>';
  $('pipelineState').textContent = 'Reasoning';
  setLayers(Object.fromEntries([...Array(10)].map((_, i) => [i + 1, 'working'])));

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        request,
        code,
        language: session.language,
        filename: session.filename,
        model: $('model').value,
        conversation: session.conversation,
      }),
    });
    const data = await response.json();
    if (!response.ok && !data.assistant_message) throw new Error(data.error || 'Request failed');

    session.conversation = Array.isArray(data.conversation) ? data.conversation : [
      ...session.conversation,
      {role:'user', content:request},
      {role:'assistant', content:data.assistant_message || data.error || 'No response.'},
    ];
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
    $('reasoning').innerHTML = `<span class="error">${esc(error.message)}</span>`;
    setLayers({1:'blocked',2:'blocked',3:'blocked',4:'waiting',5:'waiting',6:'waiting',7:'waiting',8:'waiting',9:'waiting',10:'waiting'});
  } finally {
    $('runBtn').disabled = false;
    $('runBtn').innerHTML = 'Send to SPS-CA <span>↗</span>';
  }
}

function newChat() {
  session = {conversation:[], code:$('code').value, language:$('language').value, filename:`main.${EXT[$('language').value] || 'txt'}`, turns:0};
  localStorage.removeItem(STORAGE_KEY);
  renderMessages();
  syncSessionMeta();
  $('request').value = '';
  $('pipelineState').textContent = 'Ready';
  $('reasoning').innerHTML = '<span>Waiting for your first request…</span>';
  $('decision').innerHTML = '<div class="empty">Start a conversation to see the Brain’s plan.</div>';
  $('capabilities').innerHTML = '<div class="empty">No capability run yet.</div>';
  $('output').textContent = session.code;
  $('diff').textContent = 'No changes in this turn.';
  $('trace').textContent = 'No trace yet.';
  renderPipeline();
}

function toggleCodeDock() {
  $('codeDock').classList.toggle('collapsed');
  $('collapseCodeBtn').textContent = $('codeDock').classList.contains('collapsed') ? 'Expand' : 'Collapse';
}

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

document.querySelectorAll('.tab').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach((item) => item.classList.remove('active'));
  button.classList.add('active');
  ['output','diff','trace'].forEach((id) => $(id).classList.toggle('hidden', id !== button.dataset.tab));
}));
$('chatForm').addEventListener('submit', sendMessage);
$('newChatBtn').addEventListener('click', newChat);
$('sampleBtn').addEventListener('click', loadSample);
$('collapseCodeBtn').addEventListener('click', toggleCodeDock);
$('attachCodeBtn').addEventListener('click', () => $('codeDock').scrollIntoView({behavior:'smooth', block:'center'}));
$('language').addEventListener('change', () => {
  session.language = $('language').value;
  session.filename = `main.${EXT[session.language] || 'txt'}`;
  syncSessionMeta();
  saveSession();
});
$('model').addEventListener('input', () => $('modelText').textContent = $('model').value);
$('code').addEventListener('input', () => { session.code = $('code').value; saveSession(); });

(function init() {
  $('language').value = session.language;
  $('code').value = session.code || $('code').value;
  $('modelText').textContent = $('model').value;
  renderMessages();
  syncSessionMeta();
  renderPipeline();
  loadArchitecture();
})();
