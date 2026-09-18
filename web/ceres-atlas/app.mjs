import {validateManifest, parseRoute, routeHash, facilityRoute, institutionRoute, filterFacilities, findFacility, listSnapshot} from './model.mjs';

const $ = id => document.getElementById(id);
let records = [], route = parseRoute(location.hash), ready = false, renderVersion = 0;
let sourceHash = '', renderedHash = null;
history.scrollRestoration = 'manual';

const DOMAINS = ['people','economy','transit','infrastructure','institutions','society'];
const BODY_DOMAINS = ['world', ...DOMAINS];
const METRICS = {
  'CER-P01': {output:'243.05 B/year', capital:'1.805 T', cargo:'12.985 M t/year', passengers:'1.001 M/year', power:'4,761 / 6,904 MW', capacity:'70,998 eq.', utilization:'0.672', trust:'.431', autonomy:'.375', family:'.477'},
  'CER-P02': {output:'202.55 B/year', capital:'1.504 T', cargo:'7.214 M t/year', passengers:'.520 M/year', power:'3,968 / 5,753 MW', capacity:'59,246 eq.', utilization:'.608', trust:'.531', autonomy:'.495', family:'.477'},
  'CER-P03': {output:'460.79 B/year', capital:'3.423 T', cargo:'35.900 M t/year', passengers:'3.013 M/year', power:'9,026 / 13,088 MW', capacity:'232,670 eq.', utilization:'.760', trust:'.431', autonomy:'.375', family:'.657'},
  'CER-P04': {output:'549.40 B/year', capital:'4.081 T', cargo:'42.804 M t/year', passengers:'3.592 M/year', power:'10,762 / 15,605 MW', capacity:'211,001 eq.', utilization:'.760', trust:'.431', autonomy:'.375', family:'.477'},
  'CER-P05': {output:'218.75 B/year', capital:'1.625 T', cargo:'8.765 M t/year', passengers:'.643 M/year', power:'4,285 / 6,213 MW', capacity:'34,784 eq.', utilization:'.624', trust:'.431', autonomy:'.361', family:'.477'}
};
const FACILITY_DATA = {
  'CER-P01': {short:'Occator Lift', residents:24914, transients:22796, workforce:83170, capacity:70998, output:243.05, capital:1.805, cost:29.17, replacement:2.076, cargo:12.98, passengers:1.001, calls:40, average:4761, peak:6904, utilization:.672, industrial:.498, trust:.431, autonomy:.375, family:.477},
  'CER-P02': {short:'Polar Terminal', residents:20762, transients:15260, workforce:69308, capacity:59246, output:202.55, capital:1.504, cost:24.31, replacement:1.730, cargo:7.21, passengers:.520, calls:40, average:3968, peak:5753, utilization:.608, industrial:.429, trust:.531, autonomy:.495, family:.477},
  'CER-P03': {short:'Belt Exchange', residents:94466, transients:82363, workforce:241151, capacity:232670, output:460.79, capital:3.423, cost:55.29, replacement:3.936, cargo:35.90, passengers:3.013, calls:71.80, average:9026, peak:13088, utilization:.760, industrial:.697, trust:.431, autonomy:.375, family:.657},
  'CER-P04': {short:'Shipyard Arc', residents:77435, transients:82926, workforce:232233, capacity:211001, output:549.40, capital:4.081, cost:65.93, replacement:4.693, cargo:42.80, passengers:3.592, calls:85.61, average:10762, peak:15605, utilization:.760, industrial:.730, trust:.431, autonomy:.375, family:.477},
  'CER-P05': {short:'Metric Anchorage', residents:11211, transients:10494, workforce:48434, capacity:34784, output:218.75, capital:1.625, cost:26.25, replacement:1.869, cargo:8.76, passengers:.643, calls:40, average:4285, peak:6213, utilization:.624, industrial:.472, trust:.431, autonomy:.361, family:.477},
};
const INSTITUTIONS = {
  'Ceres Commonwealth': {id:'inst:ceres-commonwealth', role:'Ultimate sovereign / local civil authority', facilities:['CER-P01','CER-P02','CER-P03','CER-P04','CER-P05']},
  'Ferrum Meridian': {id:'inst:ferrum-meridian', role:'Operator in inspected profiles', facilities:['CER-P01','CER-P02']},
  'Ceres Volatiles Cooperative': {id:'inst:ceres-volatiles-cooperative', role:'Administrator', facilities:['CER-P02']},
  'Belt Transit Authority': {id:'inst:belt-transit-authority', role:'Administrator', facilities:['CER-P03','CER-P04']},
  'Concord Mutual Infrastructure & Assurance': {id:'inst:concord-mutual', role:'Operator', facilities:['CER-P03']},
  'Asteria Ship Systems': {id:'inst:asteria-ship-systems', role:'Operator', facilities:['CER-P04']},
  'Belt Standards Directorate': {id:'inst:belt-standards-directorate', role:'Administrator', facilities:['CER-P05']},
  'Axiom Precision & Metrology': {id:'inst:axiom-precision', role:'Operator', facilities:['CER-P05']},
  'Belt Security & Rescue Directorate': {id:'inst:belt-security', role:'Security provider', facilities:['CER-P01','CER-P02','CER-P03','CER-P04','CER-P05']}
};
function instButton(name) { const info=INSTITUTIONS[name]; if(!info) return element('span',name); const b=button(name,()=>openInstitution(info.id), 'entity-link'); b.dataset.entity=name; return b; }
function openInstitution(id) { const snapshot=saveList({focus:'institution-'+id}); route=institutionRoute(route,id); history.pushState({atlas:snapshot,fromList:true},'',routeHash(route)); render(); }
function metricBar(label,value,width,action) { const row=element('div',undefined,'bar-row'); const labelNode=action?instButton(label):element('span',label); const bar=element('span',undefined,'bar'); const fill=element('i'); fill.style.width=`${width}%`; bar.append(fill); row.append(labelNode,bar,element('strong',value)); return row; }


function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function button(text, action, className) {
  const node = element('button', text, className);
  node.type = 'button';
  node.addEventListener('click', action);
  return node;
}

function image(record, detail = false) {
  const box = element('span', undefined, 'media');
  const img = element('img');
  const fallback = element('span', 'Image unavailable. Facility details remain available.', 'image-fallback');
  fallback.hidden = true;
  // Card text already names the image; detail gets the complete accessible label.
  img.alt = detail ? `${record.name} — approved reference image` : '';
  img.decoding = 'async';
  img.loading = detail ? 'eager' : 'lazy';
  img.addEventListener('error', () => { img.hidden = true; fallback.hidden = false; });
  img.addEventListener('load', () => { img.hidden = false; fallback.hidden = true; });
  img.src = record.image;
  box.append(img, fallback);
  return box;
}

function saveList(overrides = {}) {
  const previous = listSnapshot(history.state?.atlas);
  const snapshot = {...previous, scroll: window.scrollY, focus: document.activeElement?.id || previous.focus, ...overrides};
  history.replaceState({...history.state, atlas: snapshot}, '', routeHash(route));
  return snapshot;
}

function openFacility(id) {
  const snapshot = saveList({focus: `open-${id}`, lastId: id});
  route = facilityRoute(route, id);
  history.pushState({atlas: snapshot, fromList: true}, '', routeHash(route));
  render();
}

function backToList() {
  if (history.state?.fromList) {
    history.back();
  } else {
    route = {...route, facilityId: ''};
    history.replaceState({atlas: listSnapshot()}, '', routeHash(route));
    render();
  }
}

function drawCards() {
  const matches = filterFacilities(records, route);
  const lastId = history.state?.atlas?.lastId;
  const items = matches.map(record => {
    const item = element('li');
    const card = button('', () => openFacility(record.id), 'facility-card');
    card.id = `open-${record.id}`;
    card.setAttribute('aria-label', `Explore ${record.name}`);
    const copy = element('span', undefined, 'card-copy');
    const identity = element('span', record.id, 'card-id');
    if (lastId === record.id) identity.append(element('span', 'Last viewed'));
    copy.append(identity, element('span', record.name, 'card-heading'),
      element('span', record.typeLabel, 'card-type'), element('span', 'Explore facility →', 'card-open'));
    card.append(image(record), copy);
    item.append(card);
    return item;
  });
  $('facilities').replaceChildren(...items);
  $('result-count').textContent = `${matches.length} of ${records.length} facilities`;
  $('empty').hidden = matches.length !== 0;
}

function addDefinition(list, label, value) {
  list.append(element('dt', label), element('dd', value));
}

function drawDetail() {
  const view = $('detail-view'); const back = button('← Back to facilities', backToList, 'back secondary'); back.id='back-to-list';
  if (route.institutionId) { drawInstitution(view, back); return; }
  if (!route.facilityId) { drawBody(view, back); return; }
  const record=findFacility(records,route.facilityId); const title=element('h1',record?.name||'Facility not found'); title.id='detail-title'; title.tabIndex=-1;
  if (!record) { view.replaceChildren(back,title,element('p',`No facility matches “${route.facilityId}” in this local collection.`)); return; }
  const m=METRICS[record.id]; const heading=element('div','', 'detail-heading'); heading.append(element('p',`CERES / ${record.id}`,'eyebrow'),title,element('p',record.typeLabel,'lede'));
  const figure=element('figure',undefined,'detail-media'); figure.append(image(record,true),element('figcaption','HERO · Approved reference imagery'));
  const retry=button('Retry image',()=>{ figure.replaceChild(image(record,true),figure.firstChild); },'secondary'); retry.setAttribute('aria-label','Retry facility image');
  const nav=element('nav',undefined,'domain-nav'); for(const d of DOMAINS){const b=button(d.toUpperCase(),()=>{route.domain=d;history.pushState(history.state,'',routeHash(route));drawDetail();});b.classList.toggle('selected',route.domain===d);nav.append(b);}
  const analysis=element('section',undefined,'analysis'); analysis.setAttribute('aria-live','polite'); const domain=route.domain||'people'; analysis.append(element('p',domain.toUpperCase(),'eyebrow'));
  const grid=element('div',undefined,'analysis-grid');
  if(domain==='people'){grid.append(metric('Resident population','Node record: source-backed; not substituted from zones'),metric('Workforce','Workforce is separate from residents and transients'),metric('Capacity equivalent',m.capacity),metric('Transient population','NULL where not available; no zero substitution'));}
  if(domain==='economy'){grid.append(metric('Annual value added',m.output),metric('Productive capital stock',m.capital),metric('Operating cost','Source-backed node field; accounting boundary unresolved'),metric('Ceres economy','Facility values are not summed into body totals'));}
  if(domain==='transit'){grid.append(metric('Cargo throughput',m.cargo),metric('Passenger movements',m.passengers),metric('Ship calls/year','Source-backed node measure'),metric('OD flows','Modeled demand proxy; not a timetable'));}
  if(domain==='infrastructure'){grid.append(metric('Power average / peak',m.power),metric('Habitable capacity',m.capacity),metric('Utilization index',m.utilization),metric('Placement',record.id==='CER-P05'?'Strategic role; physical placement unverified':record.typeLabel));}
  if(domain==='institutions'){grid.append(metricNode('Civil authority','Ceres Commonwealth'),metricNode('Administrator',record.id==='CER-P01'?'Ceres Commonwealth':record.id==='CER-P02'?'Ceres Volatiles Cooperative':record.id==='CER-P03'||record.id==='CER-P04'?'Belt Transit Authority':'Belt Standards Directorate'),metricNode('Operator',record.id==='CER-P01'||record.id==='CER-P02'?'Ferrum Meridian':record.id==='CER-P03'?'Concord Mutual Infrastructure & Assurance':record.id==='CER-P04'?'Asteria Ship Systems':'Axiom Precision & Metrology'),metricNode('Security','Belt Security & Rescue Directorate'));}
  if(domain==='society'){grid.append(metric('Institutional trust',m.trust),metric('Political autonomy',m.autonomy),metric('Family viability',m.family),metric('Model boundary','Gameplay indices, not surveys or endorsements'));}
  analysis.append(grid,element('p','Source-backed 2226 model layer. Values retain their original grain and limitations; NULL is not zero.','source-note'));
  const facts=element('dl',undefined,'facts'); for(const [l,v] of [['Facility ID',record.id],['Facility type',record.typeLabel]]){const g=element('div');addDefinition(g,l,v);facts.append(g)}
  const prov=element('details',undefined,'provenance');const defs=element('dl');for(const [l,v] of [['Manifest','docs/ceres/manifest.json'],['Manifest SHA-256',sourceHash],['Knowledge noun ID',record.nounId],['Asset ID',record.assetId],['Media key',record.mediaKey],['Review status',record.review],['Image SHA-256',record.hash],['Image bytes',String(record.bytes)]] )addDefinition(defs,l,v);prov.append(element('summary','Identity & image provenance'),defs);
  view.replaceChildren(back,heading,figure,retry,nav,analysis,facts,element('p','No fabricated population, economic, ownership, coordinate or transit values are displayed.','muted'),prov); document.title=`${record.name} · Ceres Atlas`;
}
function bodySubnav(items, selected) {
 const nav=element('div',undefined,'subnav');
 for(const item of items){const [key,label]=Array.isArray(item)?item:[item.toLowerCase().replace(/[^a-z]+/g,'-'),item];const active=key===selected;const b=button(label,()=>{route.metric=key;history.pushState(history.state,'',routeHash(route));drawBody($('detail-view'),null);},active?'selected':'');b.setAttribute('aria-pressed',String(active));nav.append(b)} return nav;
}
function sourceBadge(text,warning=false){return element('span',text,warning?'source-badge warning':'source-badge')}
function facilityComparisons(key,format,domain,secondKey=null) {
 const wrap=element('div',undefined,'comparisons'); const values=Object.values(FACILITY_DATA).map(v=>Math.max(v[key]||0,secondKey?v[secondKey]||0:0)); const max=Math.max(...values);
 for(const record of records){const data=FACILITY_DATA[record.id];const row=button('',()=>openFacility(record.id),'comparison-row');row.setAttribute('aria-label',`Open ${record.name} dossier on ${domain}`);const top=element('span',undefined,'comparison-label');top.append(element('span',data.short),element('strong',format(data[key],secondKey?data[secondKey]:undefined)));const track=element('span',undefined,'comparison-track');const fill=element('i');fill.style.width=`${(data[key]/max)*100}%`;track.append(fill);row.append(top,track);if(secondKey){const track2=element('span',undefined,'comparison-track light');const fill2=element('i');fill2.style.width=`${(data[secondKey]/max)*100}%`;track2.append(fill2);row.append(track2)}wrap.append(row)} return wrap;
}
function topologySection(){
 const schematic=element('section',undefined,'topology'); const label=element('div',undefined,'section-heading');label.append(element('div',undefined),sourceBadge('SCHEMATIC'));label.firstChild.append(element('p','INTERACTIVE SPATIAL INDEX','eyebrow'),element('h2','Ceres network'));schematic.append(label);
 const diagram=element('div',undefined,'topology-diagram'); diagram.setAttribute('role','group'); diagram.setAttribute('aria-label','Ceres-centered facility topology');diagram.append(element('span','CERES','topology-center'));
 const points=[['CER-P01','Occator','topology-p1'],['CER-P02','Polar Terminal','topology-p2'],['CER-P03','Belt Exchange','topology-p3'],['CER-P04','Shipyard Arc','topology-p4'],['CER-P05','Metric Anchorage*','topology-p5']];
 for(const [id,label,cls] of points){const r=findFacility(records,id);const b=button(label,()=>openFacility(id),`topology-node ${cls}`);b.id=`topology-${id}`;b.setAttribute('aria-label',`${r?.name||label} facility`);diagram.append(b)}schematic.append(diagram,element('p','Topology only · not to scale. Metric Anchorage placement remains unverified.','source-note'));return schematic;
}
function drawBody(view,back){
 const domain=route.domain||'world'; const defaults={world:'environment',people:'composition',economy:'output',transit:'cargo',infrastructure:'power',institutions:'authority',society:'trust'}; const selected=route.metric||defaults[domain]; const title=element('h1','Ceres');title.id='detail-title';title.tabIndex=-1;
 const identity=element('section',undefined,'body-identity');identity.append(element('p','SOL / MAIN BELT / DWARF PLANET','eyebrow'));
 if(domain==='world'){
  const hero=element('figure',undefined,'hero-ceres');const heroImage=element('img');const heroFallback=element('span','Approved Ceres WORLD HERO unavailable. No substitute is shown.','image-fallback');heroImage.alt='Ceres — approved WORLD reference image';heroImage.src='/assets/ceres-world-hero.png';heroImage.addEventListener('error',()=>{heroImage.hidden=true;heroFallback.hidden=false});heroImage.addEventListener('load',()=>{heroImage.hidden=false;heroFallback.hidden=true});heroFallback.hidden=true;hero.append(heroImage,heroFallback,element('figcaption','HERO · APPROVED_REFERENCE · asset 0e516224-6345-4e97-b6d1-569bf193f495'));identity.append(hero,title,element('p','The physical world. The inhabited world.','lede'));
 } else { title.className='sr-only'; identity.append(title); }
 const headline=element('section',undefined,'headline-metrics');const hg=element('div',undefined,'headline-grid');for(const [l,v,n] of [['Resident population','12.186M','Biological + synthetic'],['Annual value added','5.508T','Model units / year'],['Productive capital','40.915T','Model stock'],['Facilities in pilot','5','Named, verified identities']]){const m=element('div',undefined,'headline-kpi');m.append(element('span',l),element('strong',v),element('small',n));hg.append(m)}headline.append(hg);
 const nav=element('nav',undefined,'domain-nav');nav.setAttribute('aria-label','Analytical navigation');nav.append(element('span','ANALYTICAL NAVIGATION','nav-label'));for(const d of BODY_DOMAINS){const b=button(d==='infrastructure'?'Systems':d[0].toUpperCase()+d.slice(1),()=>{route.domain=d;route.metric='';route.collection='';history.pushState(history.state,'',routeHash(route));drawBody(view,back);});b.classList.toggle('selected',domain===d);nav.append(b)}
 const section=element('section',undefined,'body-analysis');
 if(domain==='world'){
  const head=element('div',undefined,'section-heading');head.append(element('h2','The world'),sourceBadge('REFERENCE'));section.append(head,bodySubnav([['environment','Environment'],['resources','Resources'],['history','2026 history']],selected),element('h3','Physical conditions'));
  const facts=element('div',undefined,'world-facts');for(const [l,v,n] of [['Diameter','≈940 km','Reference dimension'],['Surface gravity','≈0.27 m/s²','≈2.8% Earth'],['Escape speed','≈0.51 km/s','Not mission Δv'],['Rotation','≈9 hours','One Ceres day']]){const f=element('div');f.append(element('span',l),element('strong',v),element('small',n));facts.append(f)}section.append(facts,element('h3','Atmosphere'),element('p','Extremely tenuous exosphere, with evidence of water vapor. Not breathable or capable of supporting unprotected human habitation.'),element('p','NASA/JPL physical reference layer; approximate values, distinct from the fictional 2226 model.','source-note'));
 }
 if(domain==='people'){
  const head=element('div',undefined,'section-heading');head.append(element('h2','People and settlement'),sourceBadge('CIVSTATE'));section.append(head,bodySubnav([['composition','Composition'],['age','Age'],['facilities','Facilities'],['zones','Zones']],selected),element('p','BODY · RECOGNIZED RESIDENTS · 2226','eyebrow'),element('h3','12.186 million'));
  const stack=element('div',undefined,'population-stack');stack.append(element('span','63.4%','bio'),element('span','36.6%','synthetic'));const counts=element('div',undefined,'population-counts');counts.append(metric('BIOLOGICAL','7.729M'),metric('SYNTHETIC','4.457M'));section.append(stack,counts);const nullRow=element('div',undefined,'fact-row');nullRow.append(element('span','Body-level transient measure'),element('strong','NULL'));section.append(nullRow,element('p','Transients are separate and absent from this body row. Age denominators and census-zone reconciliation remain unresolved.','source-note'),element('h3','Facility residents'),facilityComparisons('residents',v=>v.toLocaleString(),'People'));
 }
 if(domain==='economy'){
  const head=element('div',undefined,'section-heading');head.append(element('h2','The economy'),sourceBadge('BODY + NODES'));section.append(head,element('p','BODY LEVEL · MONETARY UNITS REQUIRE FINAL DEFINITION','eyebrow'),element('h3','5.508T / year'),element('p','Annual value added'),bodySubnav([['output','Output'],['capital','Capital'],['cost','Op. cost']],selected),element('h3','Annual flows · common scale'));
  section.append(metricBar('Value added','5.508T / yr',100),metricBar('Investment','1.487T / yr',27),element('p','Not stacked: production and investment are distinct annual flows.','source-note'),element('h3','Capital and economic indicators'));
  for(const [l,v] of [['Productive capital','40.915T'],['Infrastructure capital','13.093T'],['Capital / annual output','7.428'],['Income per capita','452,034'],['Productivity index','8.237']]){const row=element('div',undefined,'fact-row');row.append(element('span',l),element('strong',v));section.append(row)}section.append(element('h3','Facility economic comparisons'),selected==='capital'?facilityComparisons('capital',v=>`${v.toFixed(3)} T`,'Economy'):selected==='cost'?facilityComparisons('cost',v=>`${v.toFixed(2)} B / year`,'Economy'):facilityComparisons('output',v=>`${v.toFixed(2)} B / year`,'Economy'));
 }
 if(domain==='transit'){
  const head=element('div',undefined,'section-heading');head.append(element('h2','Movement and exchange'),sourceBadge('NODE DATA'));section.append(head,element('p','Compare a single unit at a time. Each row opens the same facility dossier on Transit.'),bodySubnav([['cargo','Cargo'],['passengers','Passengers'],['calls','Ship calls']],selected),selected==='passengers'?facilityComparisons('passengers',v=>`${v.toFixed(3)} M / year`,'Transit'):selected==='calls'?facilityComparisons('calls',v=>`${v.toFixed(2)} / year`,'Transit'):facilityComparisons('cargo',v=>`${v.toFixed(2)} M tonnes / year`,'Transit'),element('h3','Origin–destination network'),sourceBadge('Endpoint validation pending',true),element('p','The source contains modeled transport flows. Ranked corridors remain withheld until endpoint and aggregation validation.','source-note'));
 }
 if(domain==='infrastructure'){
  const head=element('div',undefined,'section-heading');head.append(element('h2','Infrastructure'),sourceBadge('FIVE NODES'));section.append(head,bodySubnav([['power','Power'],['capacity','Capacity'],['utilization','Utilization']],selected),element('h3',selected==='capacity'?'Habitable capacity':selected==='utilization'?'Utilization index':'Average and peak demand'),element('p',selected==='power'?'MW · matching operational measures, shared scale':'Five facility-node measures on a shared scale'),selected==='capacity'?facilityComparisons('capacity',v=>`${v.toLocaleString()} eq.`,'Infrastructure'):selected==='utilization'?facilityComparisons('utilization',v=>v.toFixed(3),'Infrastructure'):facilityComparisons('peak',(peak,average)=>`${average} / ${peak} MW`,'Infrastructure','average'),element('p','Dark bar: peak. Light bar: average. Higher demand alone is not a reliability judgment.','source-note'));
 }
 if(domain==='institutions'){
  const head=element('div',undefined,'section-heading');head.append(element('h2','Institutions'),sourceBadge('NAMED ROLES'));section.append(head,bodySubnav([['authority','Authority'],['influence','Influence']],selected));const common=element('div',undefined,'institution-common');common.append(element('span','COMMON CIVIL AUTHORITY'),instButton('Ceres Commonwealth'),element('p','Named ultimate sovereign and local civil authority in the five inspected facility governance profiles.'));section.append(common,element('p',"The Commonwealth's civil role, facility administration, operations and security remain distinct.",'source-note'));
  const roles=[['CER-P01','Ceres Commonwealth','Ferrum Meridian'],['CER-P02','Ceres Volatiles Cooperative','Ferrum Meridian'],['CER-P03','Belt Transit Authority','Concord Mutual Infrastructure & Assurance'],['CER-P04','Belt Transit Authority','Asteria Ship Systems'],['CER-P05','Belt Standards Directorate','Axiom Precision & Metrology']];for(const [id,admin,operator] of roles){const r=findFacility(records,id);const card=element('article',undefined,'governance-card');card.append(button(r.name,()=>openFacility(id),'facility-name'),element('span','ADMINISTRATION'),instButton(admin),element('span','OPERATOR'),instButton(operator));section.append(card)}section.append(element('p','Common named security provider: Belt Security & Rescue Directorate. Primary financier and certifier fields are NULL in these inspected profiles.','source-note'));
 }
 if(domain==='society'){
  const head=element('div',undefined,'section-heading');head.append(element('h2','Society'),sourceBadge('MODEL INDICES',true));section.append(head,element('p','Facility-specific social states; not surveys or a calculated Ceres-wide average.'),bodySubnav([['trust','Trust'],['autonomy','Autonomy'],['family','Family']],selected),element('h3',selected==='autonomy'?'Political autonomy':selected==='family'?'Family viability':'Institutional trust'),facilityComparisons(selected,v=>v.toFixed(3),'Society'),element('p','0 · Index minimum                                      1 · Index maximum','scale-note'),element('h3','Further social measures'),element('p','The source inventory also includes migration dependence, automation exposure, access scarcity, cultural distance and cognitive-sovereignty pressure, alongside separate social-pressure records.'),element('p','Fictional model indices, not measured public-opinion percentages.','source-note'));
 }
 view.replaceChildren(identity,headline,nav,section,topologySection());document.title=`${domainTitle(domain)} · Ceres Atlas`;
}
function domainTitle(d){return ({world:'Ceres world dossier',people:'People and settlement',economy:'The economy',transit:'Movement and exchange',infrastructure:'Infrastructure',institutions:'Institutions',society:'Society'})[d]||'Ceres world dossier'}
function metric(label,value){const d=element('div',undefined,'metric');d.append(element('span',label),element('strong',value));return d}
function metricNode(label,name,note=''){
 const d=element('div',undefined,'metric'); const link=instButton(name);
 if(link.tagName==='BUTTON') link.setAttribute('aria-label',`Open institution dossier: ${name}`);
 d.append(element('span',label),link); if(note) d.append(element('small',note,'metric-note')); return d;
}
function drawInstitution(view,back){const info=Object.values(INSTITUTIONS).find(x=>x.id===route.institutionId);const title=element('h1',info?Object.keys(INSTITUTIONS).find(k=>INSTITUTIONS[k]===info):'Institution not found');title.id='detail-title';title.tabIndex=-1;if(!info){view.replaceChildren(back,title,element('p','No institution relationship matches this route.'));return}const body=element('div',undefined,'analysis');body.append(element('p','INSTITUTION / GOVERNANCE','eyebrow'),element('p',info.role,'lede'),element('p','Source-backed relationship dossier. This record is not a claim of ownership, equity or sovereignty beyond its named relationship.','source-note'));const list=element('div',undefined,'analysis-grid');for(const id of info.facilities){const r=findFacility(records,id);const d=element('div',undefined,'metric');const b=button(r.name,()=>openFacility(r.id),'entity-link');d.append(element('span','Connected facility'),b);list.append(d)}body.append(list,element('p','Provenance: inspected CIVSTATE governance profile relationship; stable facility IDs retained internally.','source-note'));view.replaceChildren(back,title,body);document.title=`${title.textContent} · Ceres Atlas`}

function render() {
  if (!ready) return;
  route = parseRoute(location.hash);
  renderedHash = location.hash;
  const version = ++renderVersion;
  const detail = !route.collection && Boolean(route.facilityId || route.institutionId || route.domain || !route.collection);
  $('list-view').hidden = detail;
  $('detail-view').hidden = !detail;
  if (detail) {
    drawDetail();
    window.scrollTo(0, 0);
    $('detail-title').focus({preventScroll: true});
  } else {
    $('search').value = route.query;
    // Preserve unknown filter URLs honestly as zero results with a visible option.
    document.querySelector('option[data-unknown]')?.remove();
    if (route.type && !records.some(record => record.type === route.type)) {
      const option = element('option', `Unknown type: ${route.type}`);
      option.value = route.type; option.dataset.unknown = 'true';
      $('type-filter').append(option);
    }
    $('type-filter').value = route.type;
    drawCards();
    document.title = 'Ceres Atlas · LOOM 2226';
    const snapshot = listSnapshot(history.state?.atlas);
    requestAnimationFrame(() => {
      if (version !== renderVersion) return;
      ($(snapshot.focus) || $('list-title')).focus({preventScroll: true});
      window.scrollTo(0, snapshot.scroll);
    });
  }
}

function filterChanged() {
  route = {query: $('search').value, type: $('type-filter').value, facilityId: '', institutionId: '', domain: '', collection: '1'};
  saveList();
  renderedHash = location.hash;
  drawCards();
}

async function load() {
  ready = false;
  $('loading').hidden = false;
  $('load-error').hidden = true;
  try {
    const response = await fetch('manifest.json', {cache: 'no-store'});
    if (!response.ok) throw new Error('The local manifest is unavailable.');
    const payload = await response.json();
    records = validateManifest(payload);
    sourceHash = payload.source_sha256;
    const options = [...new Set(records.map(record => record.type))].map(type => {
      const option = element('option', records.find(record => record.type === type).typeLabel);
      option.value = type; return option;
    });
    const all = element('option', 'All types'); all.value = '';
    $('type-filter').replaceChildren(all, ...options);
    ready = true;
    $('loading').hidden = true;
    render();
  } catch {
    $('loading').hidden = true;
    $('load-error').hidden = false;
    $('error-message').textContent = 'Keep the Ceres Atlas launcher running, then try again. A missing or unverified manifest cannot be displayed.';
    $('error-title').focus();
  }
}

$('search').addEventListener('input', filterChanged);
$('type-filter').addEventListener('change', filterChanged);
$('clear-filters').addEventListener('click', () => {
  $('search').value = ''; $('type-filter').value = '';
  filterChanged(); $('search').focus(); saveList();
});
$('retry-load').addEventListener('click', load);
document.querySelector('.skip-link').addEventListener('click', event => {
  event.preventDefault(); $('main').focus();
});
document.addEventListener('keydown', event => {
  if (ready && route.facilityId && event.key === 'Escape' && !event.defaultPrevented) {
    event.preventDefault(); backToList();
  }
});
for (const name of ['popstate', 'hashchange']) window.addEventListener(name, () => {
  if (location.hash !== renderedHash) render();
});
window.addEventListener('pagehide', () => { if (ready && !route.facilityId) saveList(); });
load();
