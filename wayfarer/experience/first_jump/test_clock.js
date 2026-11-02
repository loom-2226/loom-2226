// Node-only presentation checks. No browser or flight physics is executed.
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const src=fs.readFileSync(__dirname+"/clock.js","utf8");
const funcs=src.slice(0,src.indexOf('$("go").onclick'))+"\nglobalThis.check={advanceClock,phaseAt,phaseFrac};";
const context={};vm.runInNewContext(funcs,context);
const {advanceClock,phaseAt,phaseFrac}=context.check;
const s={
 phase:"preburn",mode:"active",next_gate:null,authorised_until_s:500,
 mission_end_s:5620,presentation_s:{preburn:29,metric:151,turn:18,trim:6},
 phase_bounds_s:{preburn:[0,500],metric:[500,5400],turn:[5400,5618],trim:[5618,5620]}
};
assert(Math.abs(advanceClock(0,14.5,s)-250)<1e-7);
assert.strictEqual(phaseAt(500,s),"preburn"); // not authorised past the burn gate
s.authorised_until_s=5618;
assert.strictEqual(phaseAt(500,s),"metric");
assert.strictEqual(phaseAt(5400,s),"turn");
assert.strictEqual(phaseAt(5618,s),"turn"); // trim not authorised yet
s.authorised_until_s=5620;
assert.strictEqual(phaseAt(5618,s),"trim");
assert.strictEqual(phaseAt(advanceClock(5350,10,s),s),"turn"); // crossing uses stage-specific pacing
assert.strictEqual(advanceClock(0,1000,s),5620);
assert.strictEqual(phaseFrac(5509,"turn",s),.5);
console.log("Clock semantics PASS: full-mission boundary, three-gate cap, automatic Metric→turn, displayed phase");
