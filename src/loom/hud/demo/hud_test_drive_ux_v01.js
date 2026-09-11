(()=>{'use strict';
const stage=document.getElementById('stage');
const cameraSel=document.getElementById('camera');
const scrubState=document.getElementById('scrubState');
if(!stage||!cameraSel||window.__loomTestDriveUxInstalled)return;
window.__loomTestDriveUxInstalled=true;
const cue=document.createElement('div');
cue.id='viewModeCue';
cue.style.cssText='position:absolute;left:50%;top:8px;transform:translateX(-50%);padding:4px 7px;background:rgba(2,8,10,.70);border:1px solid #244;color:#7fd7d0;font:8px/1.2 ui-monospace,monospace;letter-spacing:.04em;pointer-events:none;z-index:4;text-align:center;white-space:nowrap';
stage.appendChild(cue);
function label(){
  if(cameraSel.value==='SHIP')return 'SHIP / LOOK';
  if(cameraSel.value==='CHASE')return 'CHASE / OWN SHIP';
  if(cameraSel.value==='TRAJECTORY'){
    const s=String(scrubState?.textContent||'');
    return s.startsWith('PREVIEW')?'TRAJECTORY / OVERVIEW':'TRAJECTORY / LOAD PLAN';
  }
  return String(cameraSel.value||'VIEW');
}
function render(){cue.textContent=label();cue.dataset.mode=cameraSel.value;}
cameraSel.addEventListener('change',render);
if(scrubState)new MutationObserver(render).observe(scrubState,{childList:true,subtree:true,characterData:true});
window.addEventListener('loom-rendezvous-quality',render);
window.addEventListener('loom-live-qualification',render);
render();
})();
