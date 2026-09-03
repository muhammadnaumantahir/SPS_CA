(() => {
  const stages = {
    request_received: ['Request received', 'SPS-CA accepted the turn and started the real backend request.'],
    rules_checked: ['Checking system rules', 'Software DNA and routing constraints are being evaluated.'],
    planning: ['Planning the task', 'Brain is selecting the intent and the smallest matching capability.'],
    capability: ['Running capability', 'The selected capability is processing the request and source.'],
    learning: ['Recording learning', 'Experience, optimization evidence, and persistent learning are being updated.'],
    complete: ['Completed', 'The response, source, trace, and learning evidence are available.'],
    running: ['Working with the local model', 'Ollama is generating the response. Local inference can take time.'],
  };
  let startedAt = 0;
  let panelTimer = null;

  function installStyles() {
    if (document.getElementById('spsProgressStyles')) return;
    const style = document.createElement('style');
    style.id = 'spsProgressStyles';
    style.textContent = `
      .sps-progress{margin:0 0 12px;padding:14px 16px;border:1px solid var(--line);border-radius:16px;background:linear-gradient(135deg,#fbfcf8,#f3f6ef);box-shadow:0 8px 28px rgba(30,35,30,.05);overflow:hidden}.sps-progress.hidden{display:none}.sps-progress-top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px}.sps-progress-title{display:flex;align-items:center;gap:9px;font-size:12px;font-weight:700}.sps-progress-dot{width:9px;height:9px;border-radius:50%;background:var(--accent);animation:spsPulse 1.5s ease-in-out infinite}.sps-progress-elapsed{font-size:10px;color:var(--muted);font-variant-numeric:tabular-nums}.sps-progress-track{height:6px;background:#e7ebe3;border-radius:999px;overflow:hidden}.sps-progress-fill{height:100%;width:8%;background:var(--accent);border-radius:999px;transition:width .35s ease}.sps-progress-stage{display:flex;gap:10px;align-items:flex-start;margin-top:12px}.sps-progress-stage-icon{flex:0 0 auto;width:24px;height:24px;display:grid;place-items:center;border-radius:8px;background:#fff;border:1px solid var(--line);font-size:12px}.sps-progress-stage-copy strong{display:block;font-size:12px;color:var(--text)}.sps-progress-stage-copy span{display:block;margin-top:3px;font-size:10px;line-height:1.45;color:var(--muted)}.sps-progress-note{margin-top:10px;font-size:9px;color:var(--muted)}
      .message.assistant .code-block,.message.assistant .chat-output-code{background:#000!important;border:1px solid #202020!important;color:#fff!important;border-radius:12px;overflow:hidden}.message.assistant .code-block .code-head,.message.assistant .chat-output-code .code-head{background:#000!important;color:#fff!important;border-bottom:1px solid #2a2a2a!important}.message.assistant .code-block .code-head span,.message.assistant .chat-output-code .code-head span{color:#fff!important}.message.assistant .code-block pre,.message.assistant .chat-output-code pre{background:#000!important;color:#fff!important;margin:0!important}.message.assistant .code-block button,.message.assistant .chat-output-code button{background:#111!important;color:#fff!important;border:1px solid #444!important}.sps-eval-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.sps-eval-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.sps-eval-button{border:1px solid var(--line);background:var(--accent);color:#fff;border-radius:10px;padding:8px 12px;cursor:pointer}.sps-eval-button.secondary{background:#fff;color:var(--text)}.sps-eval-check{font-size:10px;color:var(--muted)}.sps-eval-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:14px 0}.sps-eval-card{border:1px solid var(--line);border-radius:12px;padding:12px;background:#fafaf7}.sps-eval-card span{display:block;font-size:9px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.sps-eval-card strong{display:block;font-size:20px;margin-top:5px}.sps-eval-table{width:100%;border-collapse:collapse;font-size:10px}.sps-eval-table th,.sps-eval-table td{padding:7px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}.sps-eval-pass{font-weight:700}.sps-eval-fail{font-weight:700}.sps-eval-empty{padding:12px 0;color:var(--muted);font-size:11px}@keyframes spsPulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.82)}}
      @media(max-width:700px){.sps-progress{border-radius:13px;padding:12px}.sps-eval-grid{grid-template-columns:repeat(2,1fr)}.sps-eval-table{font-size:9px}}
    `;
    document.head.appendChild(style);
  }

  function ensurePanel() {
    let panel = document.getElementById('spsProgress');
    if (panel) return panel;
    const composer = document.getElementById('chatForm');
    if (!composer?.parentNode) return null;
    installStyles();
    panel = document.createElement('section');
    panel.id = 'spsProgress';
    panel.className = 'sps-progress hidden';
    composer.parentNode.insertBefore(panel, composer);
    return panel;
  }

  function elapsedText() {
    const seconds = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
    return seconds < 60 ? `${seconds}s` : `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  }

  function renderStage(key, percent) {
    const panel = ensurePanel();
    if (!panel) return;
    const stage = stages[key] || stages.running;
    panel.innerHTML = `<div class="sps-progress-top"><div class="sps-progress-title"><i class="sps-progress-dot"></i><span>SPS-CA is working</span></div><span class="sps-progress-elapsed">${elapsedText()}</span></div><div class="sps-progress-track"><div class="sps-progress-fill" style="width:${Math.max(5,Math.min(100,percent||10))}%"></div></div><div class="sps-progress-stage"><div class="sps-progress-stage-icon">→</div><div class="sps-progress-stage-copy"><strong>${stage[0]}</strong><span>${stage[1]}</span></div></div><div class="sps-progress-note">These updates come from the running server request, not a fake client-only timer.</div>`;
    panel.classList.remove('hidden');
  }

  function startProgress() {
    startedAt = Date.now();
    renderStage('request_received', 8);
    clearInterval(panelTimer);
    panelTimer = setInterval(() => renderStage('running', 35), 1500);
  }

  function stopProgress(success = true) {
    clearInterval(panelTimer);
    panelTimer = null;
    const panel = document.getElementById('spsProgress');
    if (!panel) return;
    renderStage(success ? 'complete' : 'running', success ? 100 : 80);
    setTimeout(() => { panel.classList.add('hidden'); panel.innerHTML = ''; }, 450);
  }

  function applyResult(d, fallbackCode) {
    state.language = d.language || 'unknown';
    state.confidence = d.language_confidence || 0;
    state.model = d.model || state.model;
    state.code = d.output_code ?? fallbackCode;
    state.conversation = (d.conversation || []).map(m => ({role:m.role,content:m.content,turnData:m.turnData}));
    const last = state.conversation.at(-1);
    if (last?.role === 'assistant') last.turnData = d;
    state.turn = Math.floor(state.conversation.length / 2);
    $('request').value = '';
    $('code').value = state.code;
    $('languageChip').textContent = `Auto · ${state.language}`;
    $('sessionTitle').textContent = d.session?.title || $('sessionTitle').textContent;
    $('turnPill').textContent = `Turn ${state.turn}`;
    renderMessages();
    renderChatInsights();
    refreshSessions().catch(() => {});
    if (state.view === 'evolution') refreshEvolution().catch(() => {});
  }

  async function readSSE(response, onEvent) {
    if (!response.body) throw new Error('Streaming is not supported by this browser.');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const {value, done} = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), {stream: !done});
      const blocks = buffer.split(/\n\n/);
      buffer = blocks.pop() || '';
      for (const block of blocks) {
        const line = block.split('\n').find(x => x.startsWith('data:'));
        if (!line) continue;
        try { onEvent(JSON.parse(line.slice(5).trim())); } catch (_) {}
      }
      if (done) break;
    }
    if (buffer.trim()) {
      const line = buffer.split('\n').find(x => x.startsWith('data:'));
      if (line) { try { onEvent(JSON.parse(line.slice(5).trim())); } catch (_) {} }
    }
  }

  async function streamingSend() {
    const request = $('request').value.trim();
    if (!request) return;
    if (!state.sessionId) await newChat();
    const code = $('code').value;
    state.code = code;
    $('sendBtn').disabled = true;
    $('sendBtn').textContent = 'Working…';
    startProgress();
    try {
      const response = await fetch('/api/chat/stream', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:state.sessionId,request,code,filename:$('filename').value||'main.py',model:state.model,conversation:state.conversation.map(m=>({role:m.role,content:m.content,turnData:m.turnData}))})});
      if (!response.ok && !response.body) { const d = await response.json().catch(() => ({})); throw new Error(d.error || `Request failed (${response.status})`); }
      let result = null;
      await readSSE(response, event => {
        if (event.type === 'stage') renderStage(event.stage, event.progress);
        if (event.type === 'result') { result = event.payload; }
        if (event.type === 'error') throw new Error(event.message || 'Streaming request failed.');
      });
      if (!result) throw new Error('Streaming request finished without a result.');
      applyResult(result, code);
      stopProgress(Boolean(result.success));
    } catch (error) {
      stopProgress(false);
      state.conversation.push({role:'assistant',content:`I could not complete this turn.\n\n${error.message}`});
      renderMessages();
    } finally {
      $('sendBtn').disabled = false;
      $('sendBtn').textContent = 'Send ↗';
    }
  }

  function evaluationSection() {
    if (document.getElementById('view-evaluation')) return;
    installStyles();
    const nav = document.querySelector('.sidebar-bottom');
    if (nav) {
      const button = document.createElement('button');
      button.className = 'side-nav';
      button.dataset.view = 'evaluation';
      button.textContent = '✓ Tests & Evidence';
      button.onclick = () => switchView('evaluation');
      nav.appendChild(button);
    }
    const main = document.querySelector('.main');
    if (!main) return;
    const section = document.createElement('section');
    section.id = 'view-evaluation';
    section.className = 'view';
    section.innerHTML = `<div class="view-head"><div><span class="eyebrow">SCENARIO LAB</span><h1>Tests & Evidence</h1><p>Run the JSON scenario suite, inspect actual results, and watch capability growth and learning evidence over time.</p></div></div><div class="analysis-card"><div class="sps-eval-head"><div><h3>Scenario suite</h3><p class="sps-eval-empty">Default suite contains 130 concrete scenarios. Results are persisted after every case.</p></div><div class="sps-eval-actions"><label class="sps-eval-check"><input id="evalLiveEvolve" type="checkbox"> allow automatic Evolution</label><button id="evalRun" class="sps-eval-button">Run full suite</button><button id="evalRefresh" class="sps-eval-button secondary">Refresh</button></div></div><div id="evalSummary" class="sps-eval-grid"></div><div id="evalImprovement"></div><div id="evalTable"></div></div>`;
    main.appendChild(section);
    document.getElementById('evalRun').onclick = async () => {
      const live = document.getElementById('evalLiveEvolve').checked;
      const button = document.getElementById('evalRun');
      button.disabled = true; button.textContent = 'Running…';
      try {
        const response = await fetch('/api/evaluation/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({live_evolve:live})});
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Could not start test suite');
        await pollEvaluation(data.run_id);
      } catch (error) { showDrawer('Test runner error',`<p>${esc(error.message)}</p>`); }
      finally { button.disabled = false; button.textContent = 'Run full suite'; }
    };
    document.getElementById('evalRefresh').onclick = () => loadEvaluation();
    loadEvaluation();
  }

  async function pollEvaluation(runId) {
    for (let i=0;i<720;i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const data = await fetch('/api/evaluation/latest').then(r=>r.json()).catch(() => null);
      if (data?.run_id === runId) renderEvaluation(data);
      if (data?.run_id === runId && data.finished_at) return;
    }
  }

  async function loadEvaluation() {
    const data = await fetch('/api/evaluation/latest').then(r=>r.json()).catch(() => null);
    if (data?.run_id) renderEvaluation(data);
    const learning = await fetch('/api/learning').then(r=>r.json()).catch(() => null);
    const host = document.getElementById('evalImprovement');
    if (host && learning) host.innerHTML = `<div class="evidence-grid"><div><span>Long-term tasks</span><strong>${esc(learning.total_tasks||0)}</strong></div><div><span>Success rate</span><strong>${Math.round(Number(learning.overall_success_rate||0)*100)}%</strong></div><div><span>Tracked capabilities</span><strong>${esc(Object.keys(learning.capabilities||{}).length)}</strong></div><div><span>Failures</span><strong>${esc(Object.keys(learning.failure_patterns||{}).length)}</strong></div></div>`;
  }

  function renderEvaluation(data) {
    const summary = document.getElementById('evalSummary');
    const table = document.getElementById('evalTable');
    if (!summary || !table) return;
    summary.innerHTML = [['Scenarios',data.total],['Passed',data.passed],['Failed',data.failed],['Pass rate',`${Math.round((data.pass_rate||0)*100)}%`],['Run',data.run_id]].map(x=>`<div class="sps-eval-card"><span>${esc(x[0])}</span><strong>${esc(x[1])}</strong></div>`).join('');
    const rows = (data.scenarios||[]).slice(-30).reverse();
    table.innerHTML = rows.length ? `<table class="sps-eval-table"><thead><tr><th>Scenario</th><th>Result</th><th>Intent</th><th>Capability</th><th>Assertions</th></tr></thead><tbody>${rows.map(row=>`<tr><td>${esc(row.scenario_id)}</td><td class="${row.passed?'sps-eval-pass':'sps-eval-fail'}">${row.passed?'PASS':'FAIL'}</td><td>${esc(row.actual?.intent||'unknown')}</td><td>${esc(row.actual?.capability_id||'none')}</td><td>${esc((row.assertion_failures||[]).join('; ')||'—')}</td></tr>`).join('')}</tbody></table>` : '<div class="sps-eval-empty">No suite result yet. Run the suite to populate evidence.</div>';
  }

  document.addEventListener('DOMContentLoaded', () => {
    evaluationSection();
    window.send = streamingSend;
  });
})();
