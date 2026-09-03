(() => {
'use strict';

const MAJOR_ENTITY_TO_TOKEN={ME:'MERCURY',VE:'VENUS',EA:'EARTH',LU:'LUNA',MA:'MARS',CER:'CERES',JU:'JUPITER_SYSTEM',SA:'SATURN_SYSTEM',UR:'URANUS_SYSTEM',NE:'NEPTUNE_SYSTEM',PL:'PLUTO_SYSTEM'};
const MAJOR_NAME_TO_TOKEN={MERCURY:'MERCURY',VENUS:'VENUS',EARTH:'EARTH',MOON:'LUNA',LUNA:'LUNA',MARS:'MARS',CERES:'CERES',JUPITER:'JUPITER_SYSTEM',SATURN:'SATURN_SYSTEM',URANUS:'URANUS_SYSTEM',NEPTUNE:'NEPTUNE_SYSTEM',PLUTO:'PLUTO_SYSTEM'};

function cleanToken(value){
  const s=String(value||'').trim().toUpperCase();
  if(!s)return null;
  return MAJOR_NAME_TO_TOKEN[s]||s.replace(/\s+/g,'_');
}

function selectedEntityRouteToken(){
  try{
    if(typeof scene==='undefined'||!scene||typeof selectedEntityId==='undefined'||!selectedEntityId)return null;
    const e=(scene.entities||[]).find(x=>x.entity_id===selectedEntityId);
    if(!e)return null;
    if(MAJOR_ENTITY_TO_TOKEN[e.entity_id])return MAJOR_ENTITY_TO_TOKEN[e.entity_id];
    for(const key of ['navigation_token','navigator_token','route_token','canonical_token','body_token']){
      const v=cleanToken(e[key]);
      if(v)return v;
    }
    if(e.entity_class==='INFRASTRUCTURE'){
      const parent=cleanToken(e.parent_entity_id);
      if(parent)return MAJOR_ENTITY_TO_TOKEN[parent]||parent;
    }
    for(const key of ['name','display_name','label','canonical_name']){
      const v=cleanToken(e[key]);
      if(v)return v;
    }
  }catch(_err){}
  const selected=document.querySelector('#selected .selname');
  return cleanToken(selected?.textContent||'');
}

function destinationFromPanel() {
  const el = document.querySelector('#flightPlanningPanel .fpDestination');
  const text = cleanToken(el?.textContent || '');
  if (!text || text === 'SELECT_ON_MAP' || text === '—') return null;
  const selected=selectedEntityRouteToken();
  // GIS entity IDs such as DAV are display/database identifiers, not necessarily
  // Navigator route tokens. When the panel destination came from the current map
  // selection, prefer the entity's authoritative navigation/name token.
  if(selected && text!==selected && !Object.values(MAJOR_NAME_TO_TOKEN).includes(text))return selected;
  return text;
}

function installPixelNavigationShim() {
  document.addEventListener('click', (event) => {
    const button = event.target && event.target.closest ? event.target.closest('#flightPlanningPanel .fpDiscover') : null;
    if (!button) return;

    const label = String(button.textContent || '').trim().toUpperCase();
    if (!label.startsWith('DISCOVER ROUTES')) return;

    const destination = destinationFromPanel();
    if (!destination) return;

    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    button.disabled = true;
    button.textContent = `OPENING ROUTE SEARCH · ${destination}`;
    const status = document.querySelector('#flightPlanningPanel .fpStatus');
    if (status) status.textContent = `STARTING NAVIGATOR · ${destination}`;

    const q = new URLSearchParams({destination, priority: 'BALANCED', ts: String(Date.now())});
    window.location.assign('/flight-planning/discover-start?' + q.toString());
  }, true);

  const params = new URLSearchParams(window.location.search);
  const jobId = params.get('fp_job');
  if (!jobId) return;

  const destination = params.get('fp_destination') || '';
  const cleanUrl = window.location.pathname;
  history.replaceState(null, '', cleanUrl);

  const waitForPlanner = () => {
    const panel = document.getElementById('flightPlanningPanel');
    if (!panel) {
      setTimeout(waitForPlanner, 100);
      return;
    }
    const status = panel.querySelector('.fpStatus');
    if (status) status.textContent = `DISCOVERING ROUTES · ${destination || 'DESTINATION'}`;

    let attempts = 0;
    const poll = async () => {
      attempts += 1;
      try {
        const response = await fetch('/flight-planning/status.json?ts=' + Date.now(), {cache: 'no-store'});
        if (!response.ok) throw new Error(`STATUS HTTP ${response.status}`);
        const data = await response.json();
        if (data.job_id !== jobId) {
          if (attempts < 180) return setTimeout(poll, 1000);
          throw new Error('route discovery job was replaced');
        }
        if (data.status === 'RUNNING') {
          if (status) status.textContent = `DISCOVERING ROUTES · ${destination || 'DESTINATION'} · ${attempts}s`;
          if (attempts < 180) return setTimeout(poll, 1000);
          throw new Error('route discovery timed out');
        }
        if (data.status === 'ERROR') throw new Error(data.error || 'Navigator discovery failed');
        if (data.status === 'COMPLETE') {
          window.location.reload();
          return;
        }
        if (attempts < 180) return setTimeout(poll, 1000);
        throw new Error('route discovery did not complete');
      } catch (err) {
        if (status) status.textContent = `ERROR · ${String(err?.message || err)}`;
      }
    };
    poll();
  };
  waitForPlanner();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', installPixelNavigationShim, {once: true});
} else {
  installPixelNavigationShim();
}
})();
