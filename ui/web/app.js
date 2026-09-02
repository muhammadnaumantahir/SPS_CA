const $ = (id) => document.getElementById(id);
const EXT = {python:'py',javascript:'js',typescript:'ts',java:'java',go:'go',csharp:'cs'};

const defaultLayers = [
  ['Software DNA layer','Acts as the absolute source of truth, defining constraints and meta-rules that all evolution must obey.'],
  ['Governance layer','Executive gatekeeper that authorizes proposed changes against the Software DNA before deployment.'],
  ['Cognitive core','Synthesizes goals and system state into tactical decisions, reasoning, and plans.'],
  ['Knowledge core','Manages structured, evolving domain knowledge.'],
  ['Experience core','Collects and stores feedback and runtime signals as historical memory.'],
  ['Meta-learning core',"Evaluates and improves the system's own learning process."],
  ['Adaptation core','Shifts behavior instantly by context, without modifying source code.'],
  ['Evolution core','The engine of genuine structural self-growth.'],
  ['Verification & Validation','Screens new or mutated code in a sandbox before it reaches production.'],
  ['Execution layer','Translates validated decisions into real, observable action.']
];

function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function chips(items=[]){return items.map(x=>`<span class="sub-chip">${esc(x)}</span>`).join('');}

function renderPipeline(layers=defaultLayers.map((x,i)=>({number:i+1,name:x[0],purpose:x[1],description:x[1],sub_components:[],status:'ready'}))){
  $('pipeline').innerHTML=layers.map(l=>`<article class="layer" data-layer="${l.number}">
    <div class="layer-top"><div class="layer-num">L${String(l.number).padStart(2,'0')}</div><div class="layer-status">${esc(l.status||'ready')}</div></div>
    <div class="layer-body"><strong>${esc(l.name)}</strong><small>${esc(l.purpose||l.description||'')}</small>
      ${l.sub_components?.length?`<div class="subcomponents"><span class="sub-label">SUB-COMPONENTS</span><div class="sub-chip-list">${chips(l.sub_components)}</div></div>`:''}
    </div></article>`).join('');
}

async function loadArchitecture(){
  try{
    const d=await fetch('/api/architecture').then(r=>r.json());
    renderPipeline(d.layers);
    $('brainProvider').textContent=d.brain.default_provider;
    $('providerText').textContent=d.brain.default_provider;
    $('architecture').innerHTML=`<div class="brain-node"><span>🧠</span><div><strong>${esc(d.brain.name)}</strong><small>${esc(d.brain.role)}</small></div><b>SEPARATE</b></div>
      <div class="boundary-arrow">↓</div>
      <div class="architecture-note"><strong>10-Layer SPS-CA Architecture</strong><span>Each layer has a defined purpose; sub-components are modular and optional.</span></div>
      <div class="layer-map">${d.layers.map(l=>`<details class="map-layer"><summary><span>L${String(l.number).padStart(2,'0')}</span><strong>${esc(l.name)}</strong><em>${l.sub_components?.length||0} components</em></summary><p>${esc(l.purpose||l.description||'')}</p><div class="sub-chip-list">${chips(l.sub_components||[])}</div></details>`).join('')}</div>
      <div class="supporting"><b>Supporting subsystems</b>${(d.supporting_subsystems||[]).map(x=>`<span>${esc(x)}</span>`).join('')}</div>`;
  }catch(e){renderPipeline();}
}

function setLayers(map={}){document.querySelectorAll('.layer').forEach(el=>{const n=el.dataset.layer;if(map[n])el.querySelector('.layer-status').textContent=map[n]});}

async function runSps(){
  const request=$('request').value.trim(),code=$('code').value;if(!request||!code)return;
  $('runBtn').disabled=true;$('runBtn').innerHTML='Brain reasoning… <span class="spinner"></span>';$('pipelineState').textContent='Processing';
  setLayers(Object.fromEntries([...Array(10)].map((_,i)=>[i+1,'working'])));
  try{
    const language=$('language').value;
    const d=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request,code,language,filename:'main.'+(EXT[language]||'txt'),model:$('model').value})}).then(async r=>{const x=await r.json();if(!r.ok)throw new Error(x.error||'Request failed');return x});
    $('pipelineState').textContent='Complete';
    const status={};(d.layers||[]).forEach(l=>status[l.number]=l.status);setLayers(status);
    $('brainProvider').textContent=d.brain.provider;$('providerText').textContent=d.brain.provider;$('modelText').textContent=d.brain.model||$('model').value;
    $('reasoning').innerHTML=`<b>Intent</b><p>${esc(d.intent)}</p><b>Reasoning</b><p>${esc(d.reasoning||'Plan produced by the Brain.')}</p>`;
    $('decision').innerHTML=`<div class="intent">${esc(d.intent)}</div><div class="decision-note">The Brain selected an ordered plan. SPS-CA capabilities execute that plan; the Brain does not execute code.</div>`;
    $('capabilities').innerHTML=(d.capability_results||d.steps||[]).map((c,i)=>`<div class="cap-item"><span>${String(i+1).padStart(2,'0')}</span><div><strong>${esc(c.name||c.capability_id)}</strong><small>${esc(c.reason||c.summary||'Selected by Brain')}</small></div><b>${esc(c.status||'planned')}</b></div>`).join('')||'<div class="empty">No capability selected.</div>';
    $('output').textContent=d.output_code||'No modified source produced.';$('diff').textContent=d.diff||'No source diff.';$('trace').textContent=JSON.stringify(d,null,2);
  }catch(e){
    $('pipelineState').textContent='Brain unavailable / failed';$('reasoning').innerHTML=`<span class="error">${esc(e.message)}</span>`;
    setLayers({1:'blocked',2:'blocked',3:'blocked',4:'waiting',5:'waiting',6:'waiting',7:'waiting',8:'waiting',9:'waiting',10:'waiting'});
  }finally{$('runBtn').disabled=false;$('runBtn').innerHTML='Run SPS-CA <span>→</span>';}
}

document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));btn.classList.add('active');['output','diff','trace'].forEach(id=>$(id).classList.toggle('hidden',id!==btn.dataset.tab));}));
$('runBtn').addEventListener('click',runSps);
$('model').addEventListener('input',()=>$('modelText').textContent=$('model').value);
$('sampleBtn').addEventListener('click',()=>{$('code').value=`def divide(a, b):\n    return a / b\n`;$('request').value='Add input validation to this function so division by zero is handled safely.'});
$('clearBtn').addEventListener('click',()=>{$('request').value='';$('pipelineState').textContent='Ready';$('reasoning').innerHTML='<span>Waiting for a request…</span>'});
renderPipeline();loadArchitecture();
