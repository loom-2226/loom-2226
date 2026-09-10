(()=>{'use strict';
if(window.__loomQualityFetchHook)return;
window.__loomQualityFetchHook=true;
const original=window.fetch.bind(window);
window.fetch=async function(...args){
  const response=await original(...args);
  try{
    const target=typeof args[0]==='string'?args[0]:(args[0]&&args[0].url)||'';
    if(target.includes('rendezvous-preview.json')){
      response.clone().json().then(payload=>{
        window.__loomRendezvousQuality=payload;
        window.dispatchEvent(new CustomEvent('loom-rendezvous-quality',{detail:payload}));
      }).catch(()=>{});
    }
  }catch(_e){}
  return response;
};
})();
