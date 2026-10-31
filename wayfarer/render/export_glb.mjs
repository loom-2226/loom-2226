import fs from 'node:fs';import crypto from 'node:crypto';
import {shapeMesh,commandMeshes,crownMeshes,MATS,MB} from './loomgl_export.mjs';
const R='../results/out/wayfarer_v05_geometry.json', B=fs.readFileSync(R),G=JSON.parse(B),sc=JSON.parse(fs.readFileSync('out/l1_scene.json'));
const sha=crypto.createHash('sha256').update(B).digest('hex');
if(sha!=='5d73cdd1d7893b75637fc3b2e8bf2d9b786b792fede277e759561643f4ee0256')throw Error('geometry mismatch');
let data=[],len=0,acc=[],bv=[],mt=[],meshes=[],nodes=[],scenes=[];
const MID=new Map();
function mat(s){if(MID.has(s))return MID.get(s);let c=MATS[s]?.c||[.5,.5,.5];let j=mt.length;mt.push({name:s,doubleSided:true,pbrMetallicRoughness:{baseColorFactor:[...c,1],metallicFactor:.1,roughnessFactor:.65}});MID.set(s,j);return j}
function add(b,target){let k=(4-len%4)%4;data.push(Buffer.alloc(k),b);len+=k+b.length;let j=bv.length;bv.push({buffer:0,byteOffset:len-b.length,byteLength:b.length,target});return j}
function mesh(s,m,b){if(!b.i.length)return null;let p=new Float32Array(b.p),n=new Float32Array(b.n),i=new Uint32Array(b.i);
 let v=add(Buffer.from(p.buffer),34962),nv=add(Buffer.from(n.buffer),34962),iv=add(Buffer.from(i.buffer),34963);
 let lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(let j=0;j<p.length;j++) {lo[j%3]=Math.min(lo[j%3],p[j]);hi[j%3]=Math.max(hi[j%3],p[j]);}
 let a=acc.length;acc.push({bufferView:v,componentType:5126,count:p.length/3,type:'VEC3',min:lo,max:hi},{bufferView:nv,componentType:5126,count:n.length/3,type:'VEC3'},{bufferView:iv,componentType:5125,count:i.length,type:'SCALAR'});
 let j=meshes.length;meshes.push({name:s,primitives:[{attributes:{POSITION:a,NORMAL:a+1},indices:a+2,material:mat(m)}]});let t=nodes.length;nodes.push({mesh:j,name:s});return t}
function scene(name,pred,open,cmd){let groups=new Map(),out=[];
 for(let p of G.parts){if(!pred(p)||(p.tags||[]).includes('no_render'))continue;if(!groups.has(p.mat))groups.set(p.mat,new MB(0));shapeMesh(groups.get(p.mat),p,{strakeSpan:0,finSpan:0});}
 for(let [m,b] of groups){let t=mesh(name+'/'+m,m,b);if(t!==null)out.push(t)}
 for(let [m,b] of Object.entries(crownMeshes({...G.crown,open:open?1:0},0))){let t=mesh(name+'/crown_'+m,m,b);if(t!==null)out.push(t)}
 if(cmd)for(let [m,b]of Object.entries(commandMeshes(sc,{xc:0,hideCrew:new Set(sc.couches.map(v=>v.id)),crown:true}))){let t=mesh(name+'/I4_'+m,m,b);if(t!==null)out.push(t)}
 scenes.push({name,nodes:out});return out.length}
let hide=new Set(['room','outfit','floor','core','avionics','pressure_hull','bulkhead','plant','equipment','manifold','frame','longeron','tunnel','drone','water','cargo']);
let e=scene('Exterior, crown closed',p=>!(p.tags||[]).includes('room')&&!hide.has(p.mat)&&!p.mat.startsWith('room_'),false,false);
let n=scene('Interior, I4 stations, crown open',p=>p.id.startsWith('i4_')||p.mat.startsWith('room_')||['floor','bulkhead','frame','couch','rail','well','corridor'].includes(p.mat),true,true);
const bin=Buffer.concat(data);let doc={asset:{version:'2.0',generator:'LOOM 2226 source-geometry MB'},scene:0,scenes,nodes,meshes,materials:mt,bufferViews:bv,accessors:acc,buffers:[{byteLength:bin.length}],extras:{geometry_sha256:sha,status:'NON-GOVERNING, physical 3D fit HOLD'}};
function pad(b,f){return Buffer.concat([b,Buffer.alloc((4-b.length%4)%4,f)])}
let j=pad(Buffer.from(JSON.stringify(doc)),32),b=pad(bin,0),head=Buffer.alloc(12),jh=Buffer.alloc(8),bh=Buffer.alloc(8);
head.writeUInt32LE(0x46546c67,0);head.writeUInt32LE(2,4);head.writeUInt32LE(28+j.length+b.length,8);
jh.writeUInt32LE(j.length,0);jh.writeUInt32LE(0x4e4f534a,4);bh.writeUInt32LE(b.length,0);bh.writeUInt32LE(0x004e4942,4);
fs.writeFileSync('out/wayfarer_I4_in_out_5d73cdd1.glb',Buffer.concat([head,jh,j,bh,b]));
console.log('GLB export',sha,e,n,meshes.length,((28+j.length+b.length)/1048576).toFixed(2),'MiB');
