(() => {
'use strict';
/* LOOM_PHASE6_MVP_DESTINATION_GUARD_V2 */

window.LOOM_FLIGHT_DESTINATION_RESOLVER='MVP_V2_WINDOW_CAPTURE';

const CANONICAL_ENDPOINTS=new Set([
  'MERCURY','VENUS','EARTH','LUNA','MARS','CERES',
  'JUPITER_SYSTEM','SATURN_SYSTEM','URANUS_SYSTEM','NEPTUNE_SYSTEM','PLUTO_SYSTEM'
]);

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

function fpPanelDestination(){
  const el=document.querySelector('#flightPlanningPanel .fpDestination');
  const text=String(el?.textContent||'').trim().toUpperCase();
  if(!text||text==='SELECT ON MAP'||text==='—')return null;
  return text;
}

function fpPlannerStatus(text){
  const status=document.querySelector('#flightPlanningPanel .fpStatus');
  if(status)status.textContent=text;
}

function fpPlannerDestination(text){
  const destination=document.querySelector('#flightPlanningPanel .fpDestination');
  if(destination)destination.textContent=text||'SELECT ON MAP';
}

function fpDiscoverButton(){
  return document.querySelector('#flightPlanningPanel .fpDiscover');
}

async function fpResolveEntity(entity){
  const response=await fetch('/flight-planning/resolve',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({entity}),
    cache:'no-store'
  });
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);
  return data;
}

function fpFallbackDescriptor(raw){
  const token=String(raw||'').trim();
  if(!token)return null;
  return {entity_id:token,name:token,display_name:token};
}

function fpStartCanonicalDiscovery(token,label){
  const button=fpDiscoverButton();
  fpPlannerDestination(token);
  fpPlannerStatus(`STARTING NAVIGATOR · ${label||token}`);
  if(button){
    button.disabled=true;
    button.textContent=`OPENING ROUTE SEARCH · ${token}`;
  }
  const q=new URLSearchParams({destination:token,priority:'BALANCED',ts:String(Date.now())});
  window.location.assign('/flight-planning/discover-start?'+q.toString());
}

async function fpResolveAndRoute(entity){
  const button=fpDiscoverButton();
  const who=entity?.display_name||entity?.name||entity?.entity_id||'SELECTION';
  if(button)button.disabled=true;
  fpPlannerStatus(`CHECKING NAVIGATION · ${who}`);
  try{
    const capability=await fpResolveEntity(entity);
    if(!capability?.selectable||!capability?.route_token){
      const label=capability?.display_name||who;
      const reason=capability?.reason||'not a Navigator route endpoint';
      fpPlannerDestination(label);
      fpPlannerStatus(`NAVIGATION UNAVAILABLE · ${label} · ${reason}`);
      if(button){
        button.disabled=true;
        button.textContent='NAVIGATION UNAVAILABLE';
      }
      return;
    }
    fpStartCanonicalDiscovery(capability.route_token,capability.display_name||who);
  }catch(err){
    fpPlannerStatus(`NAVIGATION CHECK FAILED · ${String(err?.message||err)}`);
    if(button)button.disabled=false;
  }
}

/*
 * Base flight_planning.js still owns the generic UI and explicit canonical
 * body picker. This guard owns only map/Atlas-derived and otherwise raw
 * destinations. Capture at window level so no legacy button handler can
 * navigate to discover-start before the authoritative resolver runs.
 */
function fpCaptureDestinationClick(event){
  const target=event.target?.closest?.('#flightPlanningPanel .fpDiscover, .fpAtlasPlanHere');
  if(!target)return;

  const label=String(target.textContent||'').trim().toUpperCase();
  if(label.startsWith('TAP DESTINATION')||label.startsWith('SELECT DESTINATION'))return;

  const panelDest=fpPanelDestination();
  const isAtlasAction=target.classList?.contains('fpAtlasPlanHere');
  const explicitlyRaw=!!panelDest&&!CANONICAL_ENDPOINTS.has(panelDest);
  const mapAction=label.startsWith('PLAN FLIGHT HERE');

  /* Canonical BODY picker choices are allowed to use the base direct path. */
  if(!isAtlasAction&&!explicitlyRaw&&!mapAction)return;

  const entity=fpSelectedEntityDescriptor()||fpFallbackDescriptor(panelDest);
  if(!entity)return;

  event.preventDefault();
  event.stopPropagation();
  event.stopImmediatePropagation();
  void fpResolveAndRoute(entity);
}

window.addEventListener('click',fpCaptureDestinationClick,true);
})();
