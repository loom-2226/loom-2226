(() => {
'use strict';

const DRAWER_ID='loomNavAtlasDrawer';
let activeMode='NAV';
let drawerMinimized=false;
let drawerHidden=false;

function buttonByText(label){
  const wanted=String(label||'').trim().toUpperCase();
  return [...document.querySelectorAll('button')].find(b=>String(b.textContent||'').trim().toUpperCase()===wanted)||null;
}

function installStyle(){
  if(document.getElementById('loomNavAtlasDrawerStyle'))return;
  const style=document.createElement('style');
  style.id='loomNavAtlasDrawerStyle';
  style.textContent=`
#${DRAWER_ID}{position:fixed;z-index:30;left:14px;bottom:74px;width:min(440px,calc(100vw - 28px));max-height:min(56vh,620px);display:flex;flex-direction:column;background:rgba(8,12,18,.965);border:1px solid rgba(148,162,183,.30);border-radius:14px;box-shadow:0 16px 46px rgba(0,0,0,.40);backdrop-filter:blur(12px);overflow:hidden;color:#b9c4d3;font:10px ui-monospace,SFMono-Regular,Menlo,monospace}
#${DRAWER_ID}[hidden]{display:none!important}
#${DRAWER_ID}.minimized .loomDrawerBody{display:none}
#${DRAWER_ID} .loomDrawerHeader{display:flex;align-items:center;gap:8px;padding:8px 9px;border-bottom:1px solid rgba(140,155,176,.18)}
#${DRAWER_ID} .loomDrawerTitle{font-weight:850;letter-spacing:.10em;color:#dce5f2;white-space:nowrap}
#${DRAWER_ID} .loomDrawerTabs{display:flex;gap:4px;flex:1}
#${DRAWER_ID} .loomDrawerTabs button{padding:5px 11px;border-radius:8px;font:850 9px ui-monospace,SFMono-Regular,Menlo,monospace}
#${DRAWER_ID} .loomDrawerTabs button.active{border-color:rgba(196,215,244,.82);background:rgba(221,233,250,.92);color:#111925}
#${DRAWER_ID} .loomDrawerChrome{display:flex;gap:4px}
#${DRAWER_ID} .loomDrawerChrome button{padding:4px 7px;font-size:8px}
#${DRAWER_ID} .loomDrawerBody{min-height:0;overflow:auto;overscroll-behavior:contain;padding:8px}
#${DRAWER_ID} .loomDrawerPane[hidden]{display:none!important}
#${DRAWER_ID} #flightPlanningPanel{position:static!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;width:auto!important;max-height:none!important;overflow:visible!important;display:block!important;padding:0!important;margin:0!important;background:transparent!important;border:0!important;border-radius:0!important;box-shadow:none!important;backdrop-filter:none!important}
#${DRAWER_ID} #flightPlanningPanel>.fpHeader{display:none!important}
#${DRAWER_ID} #flightPlanningPanel .fpBody{display:block!important}
#${DRAWER_ID} #flightPlanningPanel .fpCandidates{max-height:24vh!important}
#${DRAWER_ID} #flightPlanningRestore{display:none!important}
#${DRAWER_ID} #selected{position:static!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;width:auto!important;max-width:none!important;min-width:0!important;margin:0!important;transform:none!important;z-index:auto!important;background:transparent!important;border:0!important;box-shadow:none!important}
#${DRAWER_ID} .loomAtlasEmpty{padding:12px 8px;color:#7f8b9d;line-height:1.5}
#loomNavAtlasRestore{position:fixed;z-index:31;left:14px;bottom:74px;padding:8px 11px;border-radius:10px;background:rgba(8,12,18,.96);color:#dbe5f3;border:1px solid rgba(190,211,241,.50);font:850 9px ui-monospace,SFMono-Regular,Menlo,monospace}
@media(max-width:700px){#${DRAWER_ID}{left:8px;right:8px;bottom:68px;width:auto;max-height:47vh;border-radius:12px}#${DRAWER_ID} .loomDrawerHeader{padding:7px}#${DRAWER_ID} .loomDrawerBody{padding:7px}#${DRAWER_ID} .loomDrawerTitle{display:none}#${DRAWER_ID} .loomDrawerTabs button{padding:5px 12px}#loomNavAtlasRestore{left:8px;bottom:68px}}
`;
  document.head.appendChild(style);
}

function setMode(mode){
  activeMode=mode==='ATLAS'?'ATLAS':'NAV';
  const drawer=document.getElementById(DRAWER_ID);
  if(!drawer)return;
  drawer.querySelector('[data-loom-pane="NAV"]').hidden=activeMode!=='NAV';
  drawer.querySelector('[data-loom-pane="ATLAS"]').hidden=activeMode!=='ATLAS';
  drawer.querySelectorAll('[data-loom-mode]').forEach(b=>b.classList.toggle('active',b.dataset.loomMode===activeMode));
  const externalNav=buttonByText('NAV');
  const externalAtlas=buttonByText('ATLAS');
  if(externalNav)externalNav.classList.toggle('active',activeMode==='NAV');
  if(externalAtlas)externalAtlas.classList.toggle('active',activeMode==='ATLAS');
}

function setHidden(hidden){
  drawerHidden=!!hidden;
  const drawer=document.getElementById(DRAWER_ID);
  const restore=document.getElementById('loomNavAtlasRestore');
  if(drawer)drawer.hidden=drawerHidden;
  if(restore)restore.hidden=!drawerHidden;
}

function installExternalToggleBridge(){
  document.addEventListener('click',event=>{
    const b=event.target&&event.target.closest?event.target.closest('button'):null;
    if(!b||b.closest('#'+DRAWER_ID))return;
    const text=String(b.textContent||'').trim().toUpperCase();
    if(text!=='NAV'&&text!=='ATLAS')return;
    setMode(text);
    setHidden(false);
  },true);
}

function ensureAtlasHost(pane){
  let selected=document.getElementById('selected');
  if(selected){
    if(selected.parentElement!==pane)pane.appendChild(selected);
    return;
  }
  if(!pane.querySelector('.loomAtlasEmpty')){
    const empty=document.createElement('div');
    empty.className='loomAtlasEmpty';
    empty.textContent='Select a body, settlement, station, or infrastructure object to inspect Atlas context.';
    pane.appendChild(empty);
  }
}

function installDrawer(){
  if(document.getElementById(DRAWER_ID))return true;
  const planner=document.getElementById('flightPlanningPanel');
  if(!planner)return false;
  installStyle();

  const drawer=document.createElement('section');
  drawer.id=DRAWER_ID;
  drawer.setAttribute('aria-label','LOOM navigation and atlas contextual drawer');
  drawer.innerHTML=`<div class="loomDrawerHeader"><div class="loomDrawerTitle">LOOM CONTEXT</div><div class="loomDrawerTabs"><button type="button" data-loom-mode="NAV">NAV</button><button type="button" data-loom-mode="ATLAS">ATLAS</button></div><div class="loomDrawerChrome"><button type="button" class="loomDrawerMin">MINIMIZE</button><button type="button" class="loomDrawerClose">CLOSE</button></div></div><div class="loomDrawerBody"><div class="loomDrawerPane" data-loom-pane="NAV"></div><div class="loomDrawerPane" data-loom-pane="ATLAS"></div></div>`;
  document.body.appendChild(drawer);

  const navPane=drawer.querySelector('[data-loom-pane="NAV"]');
  const atlasPane=drawer.querySelector('[data-loom-pane="ATLAS"]');
  navPane.appendChild(planner);
  ensureAtlasHost(atlasPane);

  const restore=document.createElement('button');
  restore.id='loomNavAtlasRestore';
  restore.type='button';
  restore.hidden=true;
  restore.textContent='NAV / ATLAS';
  document.body.appendChild(restore);

  drawer.querySelectorAll('[data-loom-mode]').forEach(b=>b.onclick=()=>setMode(b.dataset.loomMode));
  drawer.querySelector('.loomDrawerMin').onclick=()=>{
    drawerMinimized=!drawerMinimized;
    drawer.classList.toggle('minimized',drawerMinimized);
    drawer.querySelector('.loomDrawerMin').textContent=drawerMinimized?'RESTORE':'MINIMIZE';
  };
  drawer.querySelector('.loomDrawerClose').onclick=()=>setHidden(true);
  restore.onclick=()=>setHidden(false);

  const oldRestore=document.getElementById('flightPlanningRestore');
  if(oldRestore)oldRestore.hidden=true;
  setMode('NAV');

  const observer=new MutationObserver(()=>ensureAtlasHost(atlasPane));
  observer.observe(document.body,{childList:true,subtree:true});
  return true;
}

function boot(){
  installExternalToggleBridge();
  let tries=0;
  const timer=setInterval(()=>{
    tries+=1;
    if(installDrawer()||tries>200)clearInterval(timer);
  },50);
}

if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
else boot();
})();
