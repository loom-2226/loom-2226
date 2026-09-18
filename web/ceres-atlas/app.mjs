import {validateManifest, parseRoute, routeHash, filterFacilities, findFacility, listSnapshot} from './model.mjs';

const $ = id => document.getElementById(id);
let records = [], route = parseRoute(location.hash), ready = false, renderVersion = 0;
let sourceHash = '', renderedHash = null;
history.scrollRestoration = 'manual';

const DOMAINS = ['people','economy','transit','infrastructure','institutions','society'];
const METRICS = {
  'CER-P01': {output:'243.05 B/year', capital:'1.805 T', cargo:'12.985 M t/year', passengers:'1.001 M/year', power:'4,761 / 6,904 MW', capacity:'70,998 eq.', utilization:'0.672', trust:'.431', autonomy:'.375', family:'.477'},
  'CER-P02': {output:'202.55 B/year', capital:'1.504 T', cargo:'7.214 M t/year', passengers:'.520 M/year', power:'3,968 / 5,753 MW', capacity:'59,246 eq.', utilization:'.608', trust:'.531', autonomy:'.495', family:'.477'},
  'CER-P03': {output:'460.79 B/year', capital:'3.423 T', cargo:'35.900 M t/year', passengers:'3.013 M/year', power:'9,026 / 13,088 MW', capacity:'232,670 eq.', utilization:'.760', trust:'.431', autonomy:'.375', family:'.657'},
  'CER-P04': {output:'549.40 B/year', capital:'4.081 T', cargo:'42.804 M t/year', passengers:'3.592 M/year', power:'10,762 / 15,605 MW', capacity:'211,001 eq.', utilization:'.760', trust:'.431', autonomy:'.375', family:'.477'},
  'CER-P05': {output:'218.75 B/year', capital:'1.625 T', cargo:'8.765 M t/year', passengers:'.643 M/year', power:'4,285 / 6,213 MW', capacity:'34,784 eq.', utilization:'.624', trust:'.431', autonomy:'.361', family:'.477'}
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
function openInstitution(id) { const snapshot=saveList({focus:'institution-'+id}); route={...route,institutionId:id,facilityId:''}; history.pushState({atlas:snapshot,fromList:true},'',routeHash(route)); render(); }
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
  history.replaceState({atlas: snapshot}, '', routeHash(route));
  return snapshot;
}

function openFacility(id) {
  const snapshot = saveList({focus: `open-${id}`, lastId: id});
  route = {...route, facilityId: id};
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
function drawBody(view,back){
 const title=element('h1','Ceres'); title.id='detail-title'; title.tabIndex=-1;
 const intro=element('p','CERES BODY / 2226','eyebrow');
 const lede=element('p','A body dossier for Ceres: physical context, historical observation and the LOOM 2226 model are kept in separate evidence layers.','lede');
 const hero=element('figure',undefined,'hero-ceres');
 const fallback=element('span','Approved Ceres WORLD HERO is unavailable in the local media snapshot. No substitute is shown.','image-fallback'); hero.append(fallback,element('figcaption','HERO · WORLD media record · unavailable locally'));
 const layers=element('section',undefined,'evidence-layers');
 for(const [label,text] of [['NASA / JPL physical Ceres','Observed dwarf planet; physical reference context only.'],['Historical observation through 2026','Historical record and observation boundary; not a 2226 forecast.'],['LOOM 2226 CIVSTATE','Fictional model state, year 2226, with source grain and derivation retained.']]) layers.append(element('div',`${label}\n${text}`,'evidence-layer'));
 const headline=element('section',undefined,'headline-metrics'); headline.append(element('h2','2226 headline metrics'));
 const hg=element('div',undefined,'analysis-grid');
 for(const [l,v] of [['Biological residents','7,729,119 persons'],['Synthetic residents','4,456,610 persons'],['Combined residents','12,185,729 persons'],['Annual value added','5.508 T model units / year'],['Productive capital','40.915 T model units'],['Pilot facilities','5 verified nodes']]) hg.append(metric(l,v));
 headline.append(hg,element('p','CIVSTATE · BODY:CERES:CERES · year 2226 · DERIV:MATERIALIZER2226. Monetary units follow the model definition; they are not presented as contemporary currency.','source-note'));
 const nav=element('nav',undefined,'domain-nav'); for(const d of DOMAINS){const b=button(d.toUpperCase(),()=>{route.domain=d;route.collection='';history.pushState(history.state,'',routeHash(route));drawBody(view,back);});b.classList.toggle('selected',route.domain===d);nav.append(b)}
 const section=element('section',undefined,'analysis'); section.append(element('p',(route.domain||'people').toUpperCase(),'eyebrow'),element('h2',domainTitle(route.domain||'people')));
 const grid=element('div',undefined,'analysis-grid');
 const bodyDomains={
  people:[['Biological residents','7,729,119 persons'],['Synthetic residents','4,456,610 persons'],['Combined residents','12,185,729 persons'],['Age structure','12,185,729 denominator unresolved; age bands available in CIVSTATE']],
  economy:[['Annual value added','5.508 T model units / year'],['Annual investment','1.487 T model units / year'],['Productive capital','40.915 T model units'],['Capital / output ratio','7.428'],['Investment / output ratio','.270'],['Productivity index','8.237'],['Income per capita','452,034 model units/person/year']],
  transit:[['Cargo comparison','Five node rows · tonnes/year'],['Passenger comparison','Five node rows · movements/year'],['Ship calls','Five node rows · calls/year'],['OD joins','No fabricated corridors or timetables']],
  infrastructure:[['Average / peak power','Five node rows · MW'],['Habitable capacity','Five node rows · capacity equivalents'],['Utilization','Five node rows · index'],['Industrial capacity','Five node rows · index']],
  institutions:[['Civil authority','Ceres Commonwealth · documented relationship'],['Governance joins','Typed institution IDs; relationship type retained'],['Facility links','Five pilot facilities'],['Authority caveat','Influence is not ownership or legal authority']],
  society:[['Institutional trust','Five facility records · model index'],['Political autonomy','Five facility records · model index'],['Family viability','Five facility records · model index'],['Social pressure','Separate records retained; no body-wide mean']]
 };
 for(const [l,v] of bodyDomains[route.domain||'people']) grid.append(metric(l,v));
 section.append(grid,element('p','Source values remain measurements where present; unresolved denominators and missingness are disclosed beside them.','source-note'));
 const schematic=element('section',undefined,'topology'); schematic.append(element('h2','Ceres facility topology'),element('p','Relationships between the five verified pilot nodes; positions are schematic and do not encode physical distance.','source-note'));
 const diagram=element('div',undefined,'topology-diagram'); diagram.setAttribute('role','group'); diagram.setAttribute('aria-label','Ceres-centered facility topology');
 const center=element('span','CERES','topology-center'); diagram.append(center);
 const points=[['CER-P01','Occator','topology-p1'],['CER-P02','Polar Terminal','topology-p2'],['CER-P03','Belt Exchange','topology-p3'],['CER-P04','Shipyard Arc','topology-p4'],['CER-P05','Metric Anchorage','topology-p5']];
 for(const [id,label,cls] of points){const r=findFacility(records,id);const b=button(label,()=>openFacility(id),`topology-node ${cls}`);b.setAttribute('aria-label',`${r?.name||label} facility`);diagram.append(b)} schematic.append(diagram);
 const browse=button('Browse facility collection',()=>{route.collection='1';route.domain='';history.pushState({atlas:listSnapshot(history.state?.atlas)},'',routeHash(route));render();},'secondary');
 view.replaceChildren(back,title,intro,lede,hero,layers,headline,nav,section,schematic,browse,element('p','Approved facility imagery and typed dossier links remain available from the topology and secondary collection.','muted')); document.title='Ceres body dossier · Ceres Atlas';
}
function domainTitle(d){return ({people:'People / demographic state',economy:'Economy / flows and stocks',transit:'Transit / node comparisons',infrastructure:'Infrastructure / capacity and power',institutions:'Institutions / governance relationships',society:'Society / model indices'})[d]||'People / demographic state'}
function metric(label,value){const d=element('div',undefined,'metric');d.append(element('span',label),element('strong',value));return d}
function metricNode(label,name){const d=element('div',undefined,'metric');d.append(element('span',label),instButton(name));return d}
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
