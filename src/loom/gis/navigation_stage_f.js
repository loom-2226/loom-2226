(() => {
'use strict';
const STAGE_F_CONTRACT='LOOM_STAGE_F_INTEGRATED_GIS_3D_V1';

function installStageFRoute3D(){
  const panel=document.getElementById('navOverlayPanel');
  if(!panel||panel.dataset.stageF3d===STAGE_F_CONTRACT)return false;
  const actions=panel.querySelector('.navActions');
  const fit=panel.querySelector('.navFit');
  if(!actions||!fit)return false;

  const button=document.createElement('button');
  button.type='button';
  button.className='nav3d';
  button.textContent='3D ROUTE';
  button.title='Fit the active route in the existing Solar GIS and switch to the oblique 3D camera';
  button.onclick=()=>{
    const oblique=document.getElementById('obl');
    if(oblique)oblique.click();
    const currentFit=panel.querySelector('.navFit');
    if(currentFit&&!currentFit.hidden)currentFit.click();
  };
  actions.insertBefore(button,actions.querySelector('.navPlay'));

  const style=document.createElement('style');
  style.id='loomStageFIntegrated3DStyles';
  style.textContent='#navOverlayPanel .nav3d{flex:1;min-width:0;padding:4px 5px;font-size:7px}';
  document.head.appendChild(style);

  const sync=()=>{button.hidden=!!fit.hidden};
  sync();
  new MutationObserver(sync).observe(fit,{attributes:true,attributeFilter:['hidden']});
  panel.dataset.stageF3d=STAGE_F_CONTRACT;
  return true;
}

if(!installStageFRoute3D()){
  const observer=new MutationObserver(()=>{
    if(installStageFRoute3D())observer.disconnect();
  });
  observer.observe(document.documentElement,{childList:true,subtree:true});
}
})();
