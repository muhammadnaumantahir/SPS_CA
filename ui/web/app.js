const $ = (id) => document.getElementById(id);
const EXT = {python:'py',javascript:'js',typescript:'ts',java:'java',go:'go',csharp:'cs'};
const STORAGE = 'sps-ca-chat-v1';
const defaultLayers = [
  ['Software DNA layer','Absolute source of truth for constraints and meta-rules'],
  ['Governance layer','Authorization, compliance and risk control'],
  ['Cognitive core','Goal synthesis, reasoning, planning and decisions'],
  ['Knowledge core','Structured, evolving domain knowledge'],
  ['Experience core','Feedback, monitoring and historical memory'],
  ['Meta-learning core','Evaluation and improvement of learning strategies'],
  ['Adaptation core','Context awareness and strategy selection'],
  ['Evolution core','Structural self-growth and capability creation'],
  ['Verification & Validation','Testing, simulation and safety evidence'],
  ['Execution layer','Controlled real-world action']
];
let state = loadState();

function esc(s=''){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function chips(items=[]){return items.map(x=>`<span class="sub-chip">${esc(x)}</span>`).join('');}
function saveState(){localStorage.setItem(STORAGE,JSON.stringify(state));}
function loadState(){try{return JSON.parse(localStorage.getItem(STORAGE))||{messages:[],conversation:[],code:'def add(a, b):\n    return a + b\n',language:'python',model:'qwen2.5-coder:7b',turns:0}}catch(e){return {messages:[],conversation:[],code:'def add(a, b):\n    return a + b\n',language:'python',model:'qwen2.5-coder:7b',turns:0}}}
function updateMeta(){
  $('turnCount').textContent=`Turn ${state.turns}`;$('sessionTurns').textContent=state.turns;
  $('sessionLanguage').textContent=state.language;$('sessionFile').textContent=`main.${EXT[state.language]||'txt'}`;
}
function renderMessages(){
  const box=$('messages');
  if(!state.messages.length)return;
  box.innerHTML=state.messages.map(m=>`<div class="message ${m.role==='user'?'user-message':'assistant-message'}">
    <div class="avatar">${m.role==='user'?'You':'SPS'}</div><div class="message-body"><div class="message-role">${m.role==='user'?'YOU':'SPS-CA'}</div><div class="message-text">${esc(m.content)}</div>${m.meta?`<div class="message-meta">${esc(m.meta)}</div>`:''}</div></div>`).join('');
  box.scrollTop=box.scrollHeight;
}
function renderPipeline(layers=defaultLayers.map((x,i)=>({number:i+1,name:x[0],purpose:x[1],description:x[1],sub_components:[],status:'ready'}))){
  $('pipeline').innerHTML=layers.map(l=>`<article class="layer" data-layer="${l.number}"><div class="layer-top"><div class="layer-num">L${String(l.number).padStart(2,'0')}</div><div class="layer-status">${esc(l.status||'ready')}</div></div><div class="layer-body"><strong>${esc(l.name)}</strong><small>${esc(l.purpose||l.description||'')}</small>${l.sub_components?.length?`<div class="subcomponents"><span class="sub-label">SUB-COMPONENTS</span><div class="sub-chip-list">${chips(l.sub_components)}</div></div>`:''}</div></article>`).join('');
}
async function loadArchitecture(){
  try{const d=await fetch('/api/architecture').then(r=>r.json());renderPipeline(d.layers);$('brainProvider').textContent=d.brain.default_provider;$('providerText').textContent=d.brain.default_provider;$('architecture').innerHTML=`<div class="brain-node"><span>🧠</span><div><strong>${esc(d.brain.name)}</strong><small>${esc(d.brain.role)}</small></div><b>SEPARATE</b></div><div class="boundary-arrow">↓</div><div class="architecture-note"><strong>10-Layer SPS-CA Architecture</strong><span>Layers define responsibilities; sub-components are modular and optional.</span></div><div class="layer-map">${d.layers.map(l=>`<details class="map-layer"><summary><span>L${String(l.number).padStart(2,'0')}</span><strong>${esc(l.name)}</strong><em>${l.sub_components?.length||0} components</em></summary><p>${esc(l.purpose||l.description||'')}</p><div class="sub-chip-list">${chips(l.sub_components||[])}</div></details>`).join('')}</div><div class="supporting"><b>Supporting subsystems</b>${(d.supporting_subsystems||[]).map(x=>`<span>${esc(x)}</span>`).join('')}</div>`;}
  catch(e){renderPipeline();}
}
function setLayers(map={}){document.querySelectorAll('.layer').forEach(el=>{const n=el.dataset.layer;if(map[n])el.querySelector('.layer-status').textContent=map[n]});}
function showLatest(data){
  $('reasoning').innerHTML=`<b>Intent</b><p>${esc(data.intent||'')}</p><b>Reasoning</b><p>${esc(data.reasoning||'Plan produced by the Brain.')}</p>`;
  $('decision').innerHTML=`<div class="intent">${esc(data.intent||'No explicit intent returned.')}</div><div class="decision-note">The Brain reasons and selects capabilities. Capabilities perform the coding operation.</div>`;
  $('capabilities').innerHTML=(data.capability_results||data.steps||[]).map((c,i)=>`<div class="cap-item"><span>${String(i+1).padStart(2,'0')}</span><div><strong>${esc(c.name||c.capability_id)}</strong><small>${esc(c.reason||c.summary||'Selected by Brain')}</small></div><b>${esc(c.status||'planned')}</b></div>`).join('')||'<div class="empty">No capability selected.</div>';
  $('output').textContent=data.output_code||state.code;$('diff').textContent=data.diff||'No source diff.';$('trace').textContent=JSON.stringify(data,null,2);
}
async function runSps(e){
  e?.preventDefault();
  const request=$('request').value.trim(),code=$('code').value.trim();if(!request||!code)return;
  const language=$('language').value;state.language=language;state.model=$('model').value;state.code=code;saveState();
  appendMessage('user',request);
  $('runBtn').disabled=true;$('runBtn').innerHTML='Thinking… <span class="spinner"></span>';$('pipelineState').textContent='Brain reasoning';
  setLayers(Object.fromEntries([...Array(10)].map((_,i)=>[i+1,'working'])));
  try{
    const d=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request,code,language,filename:'main.'+(EXT[language]||'txt'),model:state.model,conversation:state.conversation})}).then(async r=>{const x=await r.json();if(!r.ok)throw new Error(x.error||'Request failed');return x});
    state.turns+=1;state.code=d.output_code||state.code;state.conversation=d.conversation||[...state.conversation,{role:'user',content:request},{role:'assistant',content:d.assistant_message||''}];saveState();
    $('code').value=state.code;appendMessage('assistant',d.assistant_message||d.reasoning||d.intent||'Done.',(d.capability_results||[]).map(x=>x.name).join(' · '));
    $('request').value='';$('pipelineState').textContent='Complete';
    const status={};(d.layers||[]).forEach(l=>status[l.number]=l.status);setLayers(status);showLatest(d);updateMeta();
  }catch(e){
    appendMessage('assistant',`I couldn't complete this turn: ${e.message}`,'Brain error');$('pipelineState').textContent='Brain unavailable / failed';$('reasoning').innerHTML=`<span class="error">${esc(e.message)}</span>`;setLayers({1:'blocked',2:'blocked',3:'blocked',4:'waiting',5:'waiting',6:'waiting',7:'waiting',8:'waiting',9:'waiting',10:'waiting'});
  }finally{$('runBtn').disabled=false;$('runBtn').innerHTML='Send to SPS-CA <span>↗</span>';$('request').focus();}
}
function appendMessage(role,content,meta=''){
  state.messages.push({role,content,meta});if(state.messages.length>40)state.messages=state.messages.slice(-40);saveState();renderMessages();updateMeta();
}
function newChat(){state={messages:[],conversation:[],code:'def add(a, b):\n    return a + b\n',language:'python',model:'qwen2.5-coder:7b',turns:0};saveState();$('code').value=state.code;$('request').value='';$('messages').innerHTML='<div class="welcome-message"><div class="welcome-icon">✦</div><div><strong>New SPS-CA session</strong><p>Start with code and a request. Continue naturally with follow-up feedback in the same conversation.</p></div></div>';$('pipelineState').textContent='Ready';updateMeta();}
$('chatForm').addEventListener('submit',runSps);
$('request').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();runSps(e)}});
$('newChatBtn').addEventListener('click',newChat);
$('model').addEventListener('input',()=>{$('modelText').textContent=$('model').value;state.model=$('model').value;saveState()});
$('language').addEventListener('change',()=>{state.language=$('language').value;updateMeta();saveState()});
$('code').addEventListener('input',()=>{state.code=$('code').value;saveState()});
$('sampleBtn').addEventListener('click',()=>{$('code').value=`def divide(a, b):\n    return a / b\n`;state.code=$('code').value;state.language='python';$('language').value='python';$('request').value='Add input validation to this function so division by zero is handled safely.';saveState();updateMeta()});
$('attachCodeBtn').addEventListener('click',()=>{$('codeDock').scrollIntoView({behavior:'smooth',block:'center'});$('code').focus()});
$('collapseCodeBtn').addEventListener('click',()=>{$('codeDock').classList.toggle('collapsed');$('collapseCodeBtn').textContent=$('codeDock').classList.contains('collapsed')?'Expand':'Collapse'});
document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));btn.classList.add('active');['output','diff','trace'].forEach(id=>$(id).classList.toggle('hidden',id!==btn.dataset.tab))}));
renderPipeline();loadArchitecture();$('code').value=state.code;$('language').value=state.language;$('model').value=state.model;$('modelText').textContent=state.model;renderMessages();updateMeta();
