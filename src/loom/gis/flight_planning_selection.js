(() => {
'use strict';

function fpSelectedEntityDescriptor(){
  try{
    if(typeof scene==='undefined'||!scene||typeof selectedEntityId==='undefined'||!selectedEntityId)return null;
    const e=(scene.entities||[]).find(x=>x.entity_id===selectedEntityId);
    if(!e)return null;
    return {
      entity_id:e.entity_id||null,
      name:e.name||e.display_name||e.label||null,
      display_name:e.display_name||e.name||e.label||null,
      entity_class:e.entity_class||null,
      parent_entity_id:e.parent_entity_id||null,
      navigation_token:e.navigation_token||e.navigator_token||e.route_token||e.canonical_token||e.body_token||null,
    };
  }catch(_err){return null;}
}

async function fpResolveEntity(entity){
  if(!entity)return null;
  const response=await fetch('/flight-planning/resolve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({entity}),cache:'no-store'});
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);
  return data;
}

function fpPlannerStatus(text){
  const status=document.querySelector('#flightPlanningPanel .fpStatus');
  if(status)status.textContent=text;
}

function fpStartResolvedDiscovery(token,label){
  const button=document.querySelector('#flightPlanningPanel .fpDiscover');
  if(button){button.disabled=true;button.textContent=`OPENING ROUTE SEARCH · ${token}`;}
  fpPlannerStatus(`STARTING NAVIGATOR · ${label||token}`);
  const q=new URLSearchParams({destination:token,priority:'BALANCED',ts:String(Date.now())});
  window.location.assign('/flight-planning/discover-start?'+q.toString());
}

async function fpPlanSelectedEntity(event){
  const target=event.target?.closest?.('#flightPlanningPanel .fpDiscover, .fpAtlasPlanHere');
  if(!target)return;
  const label=String(target.textContent||'').trim().toUpperCase();
  if(!(label.startsWith('PLAN FLIGHT HERE')||label.startsWith('DISCOVER ROUTES')))return;
  const entity=fpSelectedEntityDescriptor();
  if(!entity)return;

  event.preventDefault();
  event.stopPropagation();
  event.stopImmediatePropagation();
  target.disabled=true;
  fpPlannerStatus(`CHECKING NAVIGATION · ${entity.display_name||entity.name||entity.entity_id||'SELECTION'}`);
  try{
    const capability=await fpResolveEntity(entity);
    if(!capability?.selectable||!capability?.route_token){
      const who=capability?.display_name||entity.display_name||entity.name||entity.entity_id||'SELECTION';
      const why=capability?.reason||'not a Navigator route endpoint';
      fpPlannerStatus(`NAVIGATION UNAVAILABLE · ${who} · ${why}`);
      target.disabled=true;
      target.textContent='NAVIGATION UNAVAILABLE';
      return;
    }
    fpStartResolvedDiscovery(capability.route_token,capability.display_name||entity.display_name||entity.name);
  }catch(err){
    fpPlannerStatus(`NAVIGATION CHECK FAILED · ${String(err?.message||err)}`);
    target.disabled=false;
  }
}

// Capture before the legacy panel handlers. This is a shared GIS behavior layer,
// not a Pixel-specific mapping shim. Navigator decides endpoint eligibility.
document.addEventListener('click',fpPlanSelectedEntity,true);
})();
