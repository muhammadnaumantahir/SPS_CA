(() => {
  const stages = [
    { title: 'Reading your request', detail: 'Understanding the task, code, and context.' },
    { title: 'Checking system rules', detail: 'Applying routing, safety, and scope constraints.' },
    { title: 'Choosing the right capability', detail: 'Selecting the smallest capability that fits the request.' },
    { title: 'Working with the local model', detail: 'Ollama is generating the response. This can take time on local hardware.' },
    { title: 'Checking the result', detail: 'Preparing the returned source and capability outcome.' },
    { title: 'Saving your turn', detail: 'Updating the conversation and working code.' },
  ];

  let originalSend = null;
  let timer = null;
  let startedAt = 0;
  let current = 0;

  function installStyles() {
    if (document.getElementById('spsProgressStyles')) return;
    const style = document.createElement('style');
    style.id = 'spsProgressStyles';
    style.textContent = `
      .sps-progress{margin:0 0 12px;padding:14px 16px;border:1px solid var(--line);border-radius:16px;background:linear-gradient(135deg,#fbfcf8,#f3f6ef);box-shadow:0 8px 28px rgba(30,35,30,.05);overflow:hidden;transition:opacity .2s ease,transform .2s ease}.sps-progress.hidden{display:none}.sps-progress-top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px}.sps-progress-title{display:flex;align-items:center;gap:9px;font-size:12px;font-weight:700}.sps-progress-dot{width:9px;height:9px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 5px color-mix(in srgb,var(--accent) 12%,transparent);animation:spsPulse 1.5s ease-in-out infinite}.sps-progress-elapsed{font-size:10px;color:var(--muted);font-variant-numeric:tabular-nums}.sps-progress-track{height:6px;background:#e7ebe3;border-radius:999px;overflow:hidden}.sps-progress-fill{height:100%;width:14%;background:var(--accent);border-radius:999px;transition:width .45s ease}.sps-progress-stage{display:flex;gap:10px;align-items:flex-start;margin-top:12px}.sps-progress-stage-icon{flex:0 0 auto;width:24px;height:24px;display:grid;place-items:center;border-radius:8px;background:#fff;border:1px solid var(--line);font-size:12px}.sps-progress-stage-copy strong{display:block;font-size:12px;color:var(--text)}.sps-progress-stage-copy span{display:block;margin-top:3px;font-size:10px;line-height:1.45;color:var(--muted)}.sps-progress-note{margin-top:10px;font-size:9px;color:var(--muted)}
      @keyframes spsPulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.82)}}
      @media(max-width:700px){.sps-progress{border-radius:13px;padding:12px}.sps-progress-top{margin-bottom:8px}}
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
    if (seconds < 60) return `${seconds}s`;
    return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  }

  function render() {
    const panel = ensurePanel();
    if (!panel) return;
    const stage = stages[Math.min(current, stages.length - 1)];
    const pct = Math.min(96, Math.round(((current + 1) / stages.length) * 100));
    panel.innerHTML = `
      <div class="sps-progress-top">
        <div class="sps-progress-title"><i class="sps-progress-dot"></i><span>SPS-CA is working</span></div>
        <span class="sps-progress-elapsed">${elapsedText()}</span>
      </div>
      <div class="sps-progress-track"><div class="sps-progress-fill" style="width:${pct}%"></div></div>
      <div class="sps-progress-stage">
        <div class="sps-progress-stage-icon">${current >= stages.length - 1 ? '↻' : '→'}</div>
        <div class="sps-progress-stage-copy"><strong>${stage.title}</strong><span>${stage.detail}</span></div>
      </div>
      <div class="sps-progress-note">The activity steps are shown while the single chat request is running; completion is confirmed when the response returns.</div>
    `;
    panel.classList.remove('hidden');
    const btn = document.getElementById('sendBtn');
    if (btn) btn.textContent = current >= 3 ? 'Working…' : 'Processing…';
  }

  function start() {
    const panel = ensurePanel();
    if (!panel) return;
    startedAt = Date.now();
    current = 0;
    render();
    clearInterval(timer);
    timer = setInterval(() => {
      current = Math.min(stages.length - 1, current + 1);
      render();
    }, 3500);
  }

  function stop() {
    clearInterval(timer);
    timer = null;
    const panel = document.getElementById('spsProgress');
    if (panel) {
      panel.classList.add('hidden');
      panel.innerHTML = '';
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    originalSend = window.send;
    if (typeof originalSend !== 'function' || window.__spsProgressWrapped) return;
    window.__spsProgressWrapped = true;
    window.send = async function wrappedSend() {
      start();
      try {
        return await originalSend();
      } finally {
        stop();
      }
    };
  });
})();
