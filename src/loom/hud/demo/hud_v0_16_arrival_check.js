(()=>{'use strict';
const scrub=document.getElementById('scrub'),scrubState=document.getElementById('scrubState'),camera=document.getElementById('camera'),resetView=document.getElementById('resetView');
if(!scrub||!scrubState)return;
const row=scrub.closest('.row');
const label=document.createElement('span');label.className='scrubstate';label.id='sizeProof';label.textContent='SIZE CHECK: load a solution';row.appendChild(label);
function button(text,pct){const b=document.createElement('button');b.textContent=text;b.dataset.previewPct=String(pct);b.onclick=()=>jump(pct);row.insertBefore(b,label);return b}
button('START',0);button('MID',50);button('ARRIVAL',100);
function readMoon(){const t=(document.getElementById('readout')?.innerText||'');const rm=t.match(/MOON RANGE\s+([0-9.]+)\s+km/i),dm=t.match(/MOON DIAM\s+([0-9.]+)°/i);return{range:rm?Number(rm[1]):NaN,diam:dm?Number(dm[1]):NaN}}
function expected(range){return Number.isFinite(range)&&range>0?2*Math.atan2(1737.4,range)*180/Math.PI:NaN}
function updateProof(){requestAnimationFrame(()=>requestAnimationFrame(()=>{const m=readMoon(),e=expected(m.range);label.textContent=Number.isFinite(e)?`SIZE CHECK: ${Math.round(m.range)} km → ${e.toFixed(2)}°${Number.isFinite(m.diam)?` (HUD ${m.diam.toFixed(2)}°)`:''}`:'SIZE CHECK: preview unavailable';}))}
function jump(pct){if(scrub.disabled){label.textContent='SIZE CHECK: solve/propagate first';return}scrub.value=String(pct);scrub.dispatchEvent(new Event('input',{bubbles:true}));if(camera){camera.value='SHIP';camera.dispatchEvent(new Event('change',{bubbles:true}))}if(resetView)resetView.click();updateProof()}
scrub.addEventListener('input',updateProof);camera?.addEventListener('change',updateProof);
const observer=new MutationObserver(()=>{if(scrubState.textContent!=='LIVE')updateProof()});observer.observe(scrubState,{childList:true,characterData:true,subtree:true});
})();