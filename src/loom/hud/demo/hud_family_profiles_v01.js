(()=>{'use strict';
const root=document.documentElement;
const hud=document.querySelector('.hud');
const stage=document.getElementById('stage');
const footer=document.querySelector('.footer');
const notice=document.getElementById('hudFamilyNotice');
if(!footer||!notice||!stage||!hud)return;

function preserveViewport(){
  const compact=window.matchMedia('(orientation: portrait), (max-height: 760px)').matches;
  if(compact){
    stage.style.minHeight='32dvh';
    footer.style.maxHeight='48dvh';
    footer.style.overflowY='auto';
    footer.style.overscrollBehavior='contain';
    hud.style.gridTemplateRows='auto minmax(32dvh,1fr) minmax(0,48dvh)';
  }else{
    stage.style.minHeight='';
    footer.style.maxHeight='';
    footer.style.overflowY='';
    footer.style.overscrollBehavior='';
    hud.style.gridTemplateRows='';
  }
}
preserveViewport();
window.addEventListener('resize',preserveViewport,{passive:true});
window.visualViewport?.addEventListener('resize',preserveViewport,{passive:true});

const rowOf=id=>document.getElementById(id)?.closest('.row')||null;
const roles={
  time:rowOf('reset'),
  flight:rowOf('camera'),
  family:rowOf('hudFamily'),
  planning:rowOf('preview'),
  rendezvous:rowOf('rendezvous'),
  scrub:rowOf('scrub'),
  quality:document.getElementById('qualityPanel'),
  navplan:document.getElementById('navFlightPlan'),
  tacticalTrack:document.getElementById('tacticalTrack'),
  telemetry:document.getElementById('readout'),
  assurance:document.getElementById('wayfarerEngineering')
};
for(const [role,node] of Object.entries(roles))if(node)node.setAttribute('data-family-role',role);
function clear(){document.querySelectorAll('[data-family-role]').forEach(n=>n.classList.remove('family-primary','family-secondary'));notice.textContent='';notice.className='family-notice';}
function primary(...names){for(const name of names){const n=roles[name];if(n)n.classList.add('family-primary')}}
function secondary(...names){for(const name of names){const n=roles[name];if(n)n.classList.add('family-secondary')}}
function apply(family){
  clear();
  if(family==='NAV / FLIGHT PLAN'){
    primary('planning','rendezvous','scrub','quality','navplan','telemetry');
    secondary('time','tacticalTrack','assurance');
    notice.textContent='NAV / FLIGHT PLAN • SAME LIVE FLIGHT DECK • TRAJECTORY / TERMINAL-STATE EMPHASIS';
  }else if(family==='TACTICAL / TRACK'){
    primary('telemetry','flight','time','tacticalTrack');
    secondary('planning','rendezvous','scrub','quality','navplan','assurance');
    notice.textContent='TACTICAL / TRACK • SAME 3D LOCAL-FLIGHT SURFACE • TRACK / RELATIVE-MOTION EMPHASIS';
  }else if(family==='TACTICAL'){
    primary('telemetry','flight','time','tacticalTrack');
    secondary('planning','rendezvous','scrub','quality','navplan','assurance');
    notice.textContent='TACTICAL • SAME 3D LOCAL-FLIGHT SURFACE • LOCAL GEOMETRY / HAZARD EMPHASIS';
  }else if(family==='SENSOR / WIDE'){
    primary('telemetry','flight');
    secondary('planning','rendezvous','scrub','quality','navplan','tacticalTrack','assurance');
    notice.textContent='SENSOR / WIDE • PRESENTATION PROFILE ONLY • RUNTIME REACQUISITION DATA NOT PRESENT IN THIS QUALIFICATION SLICE';
    notice.classList.add('warn');
  }else if(family==='NAV / METRIC'){
    primary('telemetry','flight');
    secondary('planning','rendezvous','scrub','quality','navplan','tacticalTrack','assurance');
    notice.textContent='NAV / METRIC • PRESENTATION PROFILE ONLY • RUNTIME PHASE DATA NOT PRESENT IN THIS QUALIFICATION SLICE';
    notice.classList.add('warn');
  }
  root.dataset.loomHudFamilyProfile=family;
}
function current(){return root.dataset.loomHudFamily||'TACTICAL / TRACK'}
window.addEventListener('loom-hud-family-applied',e=>apply(e?.detail?.family||current()));
new MutationObserver(()=>apply(current())).observe(root,{attributes:true,attributeFilter:['data-loom-hud-family']});
apply(current());
})();
