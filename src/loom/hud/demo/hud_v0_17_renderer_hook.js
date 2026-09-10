(()=>{'use strict';
if(!window.THREE||window.__loomRendererHookInstalled)return;
window.__loomRendererHookInstalled=true;
const Original=THREE.WebGLRenderer;
function HookedWebGLRenderer(...args){
  const renderer=new Original(...args);
  const realRender=renderer.render.bind(renderer);
  renderer.render=function(scene,camera){
    window.__loomActiveScene=scene;
    window.__loomActiveCamera=camera;
    if(typeof window.__loomBeforeRender==='function')window.__loomBeforeRender(scene,camera);
    return realRender(scene,camera);
  };
  return renderer;
}
HookedWebGLRenderer.prototype=Original.prototype;
try{Object.setPrototypeOf(HookedWebGLRenderer,Original)}catch(_e){}
THREE.WebGLRenderer=HookedWebGLRenderer;
})();
