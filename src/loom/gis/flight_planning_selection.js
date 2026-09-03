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

function fpPlannerStatus(text){
  const status=document.querySelector('#flightPlanningPanel .fpStatus');
  if(status)status.textContent=text;
}

function fpPanelDestination(){
  const el=document.querySelector('#flightPlanningPanel .fpDestination');
  const text=String(el?.textContent||'').trim().toUpperCase();
  if(!text||text==='SELECT ON MAP'||text==='—')return null;
  return text;
}

function fpStartResolvedDiscovery(token,label){
  const button=document.querySelector('#flightPlanningPanel .fpDiscover');
  if(button){
    button.disabled=true;
    button.textContent=`OPENING ROUTE SEARCH · ${token}`;
  }
  fpPlannerStatus(`STARTING NAVIGATOR · ${label||token}`);
  const q=new URLSearchParams({destination:token,priority:'BALANCED',ts:String(Date.now())});
  window.location.assign('/flight-planning/discover-start?'+q.toString());
}

async function fpResolveSelectedAndDiscover(){
  const entity=fpSelectedEntityDescriptor();
  if(!entity)return false;
  const button=document.querySelector('#flightPlanningPanel .fpDiscover');
  if(button)button.disabled=true;
  fpPlannerStatus(`CHECKING NAVIGATION · ${entity.display_name||entity.name||entity.entity_id||'SELECTION'}`);
  try{
    const capability=await fpResolveEntity(entity);
    if(!capability?.selectable||!capability?.route_token){
      const who=capability?.display_name||entity.display_name||entity.name||entity.entity_id||'SELECTION';
      const why=capability?.reason||'not a Navigator route endpoint';
      fpPlannerStatus(`NAVIGATION UNAVAILABLE · ${who} · ${why}`);
      if(button){
        button.disabled=true;
        button.textContent='NAVIGATION UNAVAILABLE';
      }
      return true;
    }
    fpStartResolvedDiscovery(capability.route_token,capability.display_name||entity.display_name||entity.name);
    return true;
  }catch(err){
    fpPlannerStatus(`NAVIGATION CHECK FAILED · ${String(err?.message||err)}`);
    if(button)button.disabled=false;
    return true;
  }
}

async function fpAuthoritativeDiscoverClick(event){
  const target=event.target?.closest?.('#flightPlanningPanel .fpDiscover, .fpAtlasPlanHere');
  if(!target)return;
  const label=String(target.textContent||'').trim().toUpperCase();
  if(label.startsWith('TAP DESTINATION')||label.startsWith('SELECT DESTINATION'))return;

  const entity=fpSelectedEntityDescriptor();
  if(!entity)return;

  // If the panel destination is a known explicit picker choice that does not
  // correspond to the currently selected map entity, leave it to the base
  // planner. Map-derived destinations must always resolve through Navigator.
  const panelDest=fpPanelDestination();
  const selectedId=String(entity.entity_id||'').toUpperCase();
  const selectedName=String(entity.name||entity.display_name||'').trim().toUpperCase().replace(/\s+/g,'_');
  const buttonLabel=label;
  const appearsMapDerived=!panelDest||panelDest===selectedId||panelDest===selectedName||buttonLabel.startsWith('PLAN FLIGHT HERE')||buttonLabel.includes(selectedId)||buttonLabel.includes(selectedName);
  if(!appearsMapDerived)return;

  event.preventDefault();
  event.stopPropagation();
  event.stopImmediatePropagation();
  await fpResolveSelectedAndDiscover();
}

function fpOwnDiscoverButton(){
  const button=document.querySelector('#flightPlanningPanel .fpDiscover');
  if(!button||button.dataset.loomAuthoritativeResolve==='1')return;
  button.dataset.loomAuthoritativeResolve='1';
  const legacy=button.onclick;
  button.onclick=async event=>{
    const label=String(button.textContent||'').trim().toUpperCase();
    if(label.startsWith('DISCOVER ROUTES')||label.startsWith('PLAN FLIGHT HERE')){
      const entity=fpSelectedEntityDescriptor();
      if(entity){
        event?.preventDefault?.();
        event?.stopPropagation?.();
        await fpResolveSelectedAndDiscover();
        return;
      }
    }
    if(typeof legacy==='function')return legacy.call(button,event);
  };
}

function fpInstallAuthoritativeSelection(){
  fpOwnDiscoverButton();
  const observer=new MutationObserver(()=>fpOwnDiscoverButton());
  observer.observe(document.documentElement,{childList:true,subtree:true});
  document.addEventListener('click',fpAuthoritativeDiscoverClick,true);
}

if(document.readyState==='loading'){
  document.addEventListener('DOMContentLoaded',fpInstallAuthoritativeSelection,{once:true});
}else{
  fpInstallAuthoritativeSelection();
}
})();
