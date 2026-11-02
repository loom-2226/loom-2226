"use strict";
/* First Jump cinematic weave. No flight, optical or relativistic computation.
   The 0.268c reference is ART DIRECTION ONLY, not a measured velocity.
   All positions and effects below are synthetic illustration. */

// The ship is located at Earth before Metric, nowhere in ordinary map space
// during Metric, and at Mars only upon completed arrival.
function metricShipState(phase, fraction) {
  if (phase === "metric") {
    if (fraction >= 1) return {body: "MA", opacity: 1};
    if (fraction < .016) return {body: "EA", opacity: 1 - fraction / .016};
    return {body: null, opacity: 0};
  }
  return ["turn", "trim", "debrief"].includes(phase)
    ? {body: "MA", opacity: 1}
    : {body: "EA", opacity: 1};
}
function smoothVisual(a,b,x) {
  const q = Math.max(0,Math.min(1,(x-a)/(b-a)));
  return q*q*(3-2*q);
}
function weaveIntensity(p) {
  return smoothVisual(0,.06,p) * (1-smoothVisual(.94,1,p));
}
// Stable synthetic stars so scrub and pause produce the same exact illustration.
const fractional=x=>x-Math.floor(x);
const visualStars=Array.from({length:86},(_,i)=>{
  const a=fractional(Math.sin((i+1)*78.23)*43758.5453);
  const b=fractional(Math.sin((i+1)*17.93)*28791.109);
  const c=fractional(Math.sin((i+1)*9.33)*14323.172);
  return {theta:a*Math.PI*2,r:.12+b*.88,weight:.35+c*.65};
});
let weaveMode="A"; // A: illustrative aberration look; B: abstract shimmer
function setWeaveMode(mode) {
  weaveMode=mode==="B"?"B":"A";
  const button=document.getElementById("weaveStyle");
  if(button)button.textContent=weaveMode==="A"?"A / ABERRATION":"B / SHIMMER";
}
function drawWeaveCanvas(phase, fraction, visible) {
  const canvas=document.getElementById("weaveStars");
  const legend=document.getElementById("weaveLegend");
  const toggle=document.getElementById("weaveStyle");
  const active=phase==="metric";
  legend.hidden=!active||!visible;
  toggle.hidden=!active||!visible;
  if(!active||!visible)return;
  legend.textContent=weaveMode==="A"
    ?"ILLUSTRATIVE / NOT CANON · 0.268c VISUAL STYLE"
    :"ILLUSTRATIVE / NOT CANON · ABSTRACT WEAVE";
  const bounds=canvas.getBoundingClientRect();
  if(bounds.width<5||bounds.height<5)return;
  const ratio=Math.min(window.devicePixelRatio||1,1.5);
  const w=Math.round(bounds.width*ratio),h=Math.round(bounds.height*ratio);
  if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h}
  const ctx=canvas.getContext("2d",{alpha:true});
  ctx.clearRect(0,0,w,h);
  const p=Math.max(0,Math.min(1,fraction));
  const strength=weaveIntensity(p);
  // Dim framing while ramping out/in, with a stable hold during transit.
  const cx=w*.53,cy=h*.45,scale=Math.max(w,h);
  if(weaveMode==="A"){
    // Stylised bowward star drift and spectral colour grading, not a
    // simulation of aberration or Doppler shift at 0.268c.
    for(const star of visualStars){
      const base=star.r*scale*.73;
      const distance=base*(1-.67*p);
      const x=cx+Math.cos(star.theta)*distance;
      const y=cy+Math.sin(star.theta)*distance*.66;
      if(x<0||y<0||x>w||y>h)continue;
      const blue=star.r<.5;
      const tint=blue?"134,211,255":"238,127,120";
      const opacity=(.2+.67*star.weight)*(.2+.8*strength);
      const vx=Math.cos(star.theta)*(.016+strength*.022)*scale;
      const vy=Math.sin(star.theta)*(.016+strength*.022)*scale*.66;
      ctx.strokeStyle="rgba("+tint+","+opacity*.58+")";
      ctx.lineWidth=(.6+star.weight*1.25)*ratio;
      ctx.beginPath();ctx.moveTo(x+vx,y+vy);ctx.lineTo(x,y);ctx.stroke();
      ctx.fillStyle="rgba("+tint+","+opacity+")";
      ctx.beginPath();ctx.arc(x,y,Math.max(.7,star.weight*1.8*ratio),0,Math.PI*2);ctx.fill();
    }
    const glow=ctx.createRadialGradient(cx,cy,2,cx,cy,scale*.25);
    glow.addColorStop(0,"rgba(82,176,255,"+(.18*strength)+")");
    glow.addColorStop(1,"rgba(82,176,255,0)");
    ctx.fillStyle=glow;ctx.fillRect(0,0,w,h);
  } else {
    const glow=ctx.createRadialGradient(cx,cy,5,cx,cy,scale*.45);
    glow.addColorStop(0,"rgba(127,177,228,"+(.22*strength)+")");
    glow.addColorStop(.55,"rgba(101,110,205,"+(.12*strength)+")");
    glow.addColorStop(1,"rgba(71,50,115,0)");
    ctx.fillStyle=glow;ctx.fillRect(0,0,w,h);
    for(let i=0;i<7;i++){
      const radius=scale*(.06+i*.045);
      ctx.strokeStyle="rgba("+(i%2?"133,211,224":"155,126,231")+","+(strength*(.1+i*.025))+")";
      ctx.lineWidth=(i%3===0?2:1)*ratio;
      ctx.beginPath();
      ctx.ellipse(cx,cy,radius,radius*.5,Math.PI*(.10+.17*p+i*.08),0,Math.PI*1.75);
      ctx.stroke();
    }
  }
}
