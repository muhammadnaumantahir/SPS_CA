const $ = (id) => document.getElementById(id);

const defaultLayers = [
  ['Software DNA layer','Identity, invariants and constraints'],
  ['Governance layer','Policy, risk and approval'],
  ['Cognitive core','Reasoning, planning and code understanding'],
  ['Knowledge core','Code, capability and system knowledge'],
  ['Experience core','Past outcomes, failures and lessons'],
  ['Meta-learning core','Strategy learning and measurement'],
  ['Adaptation core','Context-sensitive strategy adjustment'],
  ['Evolution core','Creation and improvement of capabilities'],
  ['Verification & Validation','Tests, sandbox and correctness evidence'],
  ['Execution layer','Controlled application of approved changes']
];

function renderPipeline(layers = defaultLayers.map((x,i)=>({number:i+1,name:x[0],description:x[1],status:'ready'}))) {
  $('pipeline').innerHTML = layers.map((l) => `
    <div class="layer" data-layer="${l.number}">
      <div class="layer-num">${String(l.number).padStart(2,'0')}</div>
      <div class="layer-body"><strong>${l.name}</strong><small>${l.description}</small></div>
      <div class="layer-status">${l.status || 'ready'}</div>
    </div>`).join('');
}

async function loadArchitecture() {
  try {
    const data = await fetch('/api/architecture').then(r=>r.json());
    renderPipeline(data.layers);
    $('brainProvider').textContent = data.brain.default_provider;
    $('providerText').textContent = data.brain.default_provider;
    $('architecture').innerHTML = `
      <div class="brain-node"><span>🧠</span><div><strong>${data.brain.name}</strong><small>${data.brain.role}</small></div><b>SEPARATE</b></div>
      <div class="boundary-arrow">↓</div>
      <div class="layer-map">${data.layers.map(l=>`<div><span>L${String(l.number).padStart(2,'0')}</span><strong>${l.name}</strong><small>${l.description}</small></div>`).join('')}</div>
      <div class="supporting"><b>Supporting subsystems</b><span>Capability Registry</span><span>Capability Lineage</span><span>LLM Provider Abstraction</span></div>`;
  } catch(e) { renderPipeline(); }
}

function setLayers(statusMap = {}) {
  document.querySelectorAll('.layer').forEach(el => {
    const n = el.dataset.layer;
    if (statusMap[n]) el.querySelector('.layer-status').textContent = statusMap[n];
  });
}

function esc(s='') { return s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

async function runSps() {
  const request = $('request').value.trim();
  const code = $('code').value;
  if (!request || !code) return;
  $('runBtn').disabled = true; $('runBtn').innerHTML = 'Brain reasoning… <span class="spinner"></span>';
  $('pipelineState').textContent = 'Processing';
  setLayers(Object.fromEntries([...Array(10)].map((_,i)=>[i+1,'working'])));
  try {
    const data = await fetch('/api/run', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
      request, code, language:$('language').value, filename:'main.'+($('language').value==='python'?'py':$('language').value), model:$('model').value
    })}).then(async r=>{const x=await r.json(); if(!r.ok) throw new Error(x.error||'Request failed'); return x;});
    $('pipelineState').textContent = 'Complete';
    const status = {}; (data.layers||[]).forEach(l=>status[l.number]=l.status); setLayers(status);
    $('brainProvider').textContent = data.brain.provider;
    $('providerText').textContent = data.brain.provider;
    $('modelText').textContent = data.brain.model || $('model').value;
    $('reasoning').innerHTML = `<b>Intent</b><p>${esc(data.intent)}</p><b>Reasoning</b><p>${esc(data.reasoning || 'Plan produced by the Brain.')}</p>`;
    $('decision').innerHTML = `<div class="intent">${esc(data.intent)}</div><div class="decision-note">The Brain selected an ordered plan. SPS-CA capabilities execute that plan; the Brain does not execute code.</div>`;
    $('capabilities').innerHTML = (data.capability_results||data.steps||[]).map((c,i)=>`<div class="cap-item"><span>${String(i+1).padStart(2,'0')}</span><div><strong>${esc(c.name||c.capability_id)}</strong><small>${esc(c.reason||c.summary||'Selected by Brain')}</small></div><b>${c.status||'planned'}</b></div>`).join('') || '<div class="empty">No capability selected.</div>';
    $('output').textContent = data.output_code || 'No modified source produced.';
    $('diff').textContent = data.diff || 'No source diff.';
    $('trace').textContent = JSON.stringify(data, null, 2);
  } catch(e) {
    $('pipelineState').textContent = 'Brain unavailable / failed';
    $('reasoning').innerHTML = `<span class="error">${esc(e.message)}</span>`;
    setLayers({3:'blocked',4:'waiting',5:'waiting',6:'waiting',7:'waiting',8:'waiting',9:'waiting',10:'waiting'});
  } finally { $('runBtn').disabled = false; $('runBtn').innerHTML = 'Run SPS-CA <span>→</span>'; }
}

document.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click',()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active')); btn.classList.add('active');
  ['output','diff','trace'].forEach(id=>$(id).classList.toggle('hidden', id!==btn.dataset.tab));
}));
$('runBtn').addEventListener('click', runSps);
$('model').addEventListener('input', ()=>$('modelText').textContent=$('model').value);
$('sampleBtn').addEventListener('click',()=>{$('code').value=`def divide(a, b):\n    return a / b\n`;$('request').value='Add input validation to this function so division by zero is handled safely.';});
$('clearBtn').addEventListener('click',()=>{$('request').value='';$('pipelineState').textContent='Ready';$('reasoning').innerHTML='<span>Waiting for a request…</span>';});
renderPipeline(); loadArchitecture();
