import {validateManifest, typeLabel, parseRoute, routeHash, facilityRoute, institutionRoute, filterFacilities, findFacility, listSnapshot} from './model.mjs';

const $ = id => document.getElementById(id);
let records = [], atlasData = null, route = parseRoute(location.hash), ready = false, renderVersion = 0;
let sourceHash = '', renderedHash = null;
history.scrollRestoration = 'manual';

const DOMAINS = ['people', 'economy', 'transit', 'infrastructure', 'institutions', 'society'];
const BODY_DOMAINS = ['world', ...DOMAINS];
const SOCIETY_METRICS = {
  trust: ['Institutional trust', 'institutional_trust'],
  autonomy: ['Political autonomy', 'political_autonomy'],
  family: ['Family viability', 'family_viability'],
  migration: ['Migration dependence', 'migration_dependence'],
  automation: ['Automation exposure', 'automation_exposure'],
  access: ['Access scarcity', 'access_scarcity'],
  cultural: ['Cultural distance', 'cultural_distance'],
  cognitive: ['Cognitive-sovereignty pressure', 'cognitive_sovereignty_pressure'],
};

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function button(text, action, className) {
  const node = element('button', text, className);
  node.type = 'button'; node.addEventListener('click', action); return node;
}
function present(value) { return value !== null && value !== undefined; }
function finite(value) { return typeof value === 'number' && Number.isFinite(value); }
function whole(value) { return finite(value) ? Math.round(value).toLocaleString('en-US') : 'Unavailable'; }
function decimal(value, places = 3) { return finite(value) ? value.toFixed(places) : 'Unavailable'; }
function scaled(value, divisor, suffix, places = 3) {
  return finite(value) ? `${(value / divisor).toFixed(places)}${suffix}` : 'Unavailable';
}
function yearOf(row) { return present(row?.year) ? String(row.year) : 'Epoch unavailable'; }
function shortName(name = '') {
  return ({
    'Occator Industrial Lift & Surface Port': 'Occator Lift',
    'Ceres Polar Volatiles Terminal': 'Polar Terminal',
    'Ceres Belt Exchange': 'Belt Exchange',
    'Ceres Shipyard Arc': 'Shipyard Arc',
    'Ceres Metric & Loom Anchorage': 'Metric Anchorage',
  })[name] || name || 'Unavailable';
}
function facilityData(id) {
  const facility = atlasData?.facilities?.[id];
  const infrastructure = facility?.infrastructure, social = facility?.social;
  return {
    short: shortName(facility?.identity?.node_name),
    residents: infrastructure?.resident_population, transients: infrastructure?.transient_daily_population,
    workforce: infrastructure?.workforce, capacity: infrastructure?.habitable_capacity,
    output: infrastructure?.annual_value_added, capital: infrastructure?.capital_stock,
    cost: infrastructure?.annual_operating_cost, replacement: infrastructure?.replacement_value,
    cargo: infrastructure?.cargo_throughput_tonnes_year, passengers: infrastructure?.passenger_movements_year,
    calls: infrastructure?.ship_calls_year, average: infrastructure?.power_average_mw,
    peak: infrastructure?.power_peak_mw, utilization: infrastructure?.utilization,
    industrial: infrastructure?.industrial_capacity_index, trust: social?.institutional_trust,
    autonomy: social?.political_autonomy, family: social?.family_viability,
    migration: social?.migration_dependence, automation: social?.automation_exposure,
    access: social?.access_scarcity, cultural: social?.cultural_distance,
    cognitive: social?.cognitive_sovereignty_pressure,
  };
}
function image(record, detail = false) {
  const box = element('span', undefined, 'media'), img = element('img');
  const fallback = element('span', 'Image unavailable. Facility details remain available.', 'image-fallback');
  fallback.hidden = true; img.alt = detail ? `${record.name} — approved reference image` : '';
  img.decoding = 'async'; img.loading = detail ? 'eager' : 'lazy';
  img.addEventListener('error', () => { img.hidden = true; fallback.hidden = false; });
  img.addEventListener('load', () => { img.hidden = false; fallback.hidden = true; });
  img.src = record.image; box.append(img, fallback); return box;
}
function saveList(overrides = {}) {
  const previous = listSnapshot(history.state?.atlas);
  const snapshot = {...previous, scroll: window.scrollY, focus: document.activeElement?.id || previous.focus, ...overrides};
  history.replaceState({...history.state, atlas: snapshot}, '', routeHash(route)); return snapshot;
}
function openFacility(id) {
  const snapshot = saveList({focus: `open-${id}`, lastId: id}); route = facilityRoute(route, id);
  history.pushState({atlas: snapshot, fromList: true}, '', routeHash(route)); render();
}
function openInstitution(id) {
  const snapshot = saveList({focus: `institution-${id}`}); route = institutionRoute(route, id);
  history.pushState({atlas: snapshot, fromList: true}, '', routeHash(route)); render();
}
function backToList() {
  if (history.state?.fromList) history.back();
  else { route = {...route, facilityId: '', institutionId: ''}; history.replaceState({atlas: listSnapshot()}, '', routeHash(route)); render(); }
}
function instButton(id, fallbackName) {
  const info = atlasData?.institutions?.[id];
  if (!info) return element('span', fallbackName || 'Unavailable');
  const name = info.name || fallbackName || 'Institution identity unavailable';
  const control = button(name, () => openInstitution(info.id), 'entity-link');
  control.dataset.entity = info.id; control.setAttribute('aria-label', `Open institution dossier: ${name}`); return control;
}
function metric(label, value, note = '') {
  const node = element('div', undefined, 'metric'); node.append(element('span', label), element('strong', value));
  if (note) node.append(element('small', note, 'metric-note')); return node;
}
function metricNode(label, relation) {
  const node = element('div', undefined, 'metric'); node.append(element('span', label));
  if (relation) {
    node.append(instButton(relation.institution_id, relation.name));
    node.append(element('small', `${relation.domain} · ${relation.control_class} · influence ${decimal(relation.weight)}`, 'metric-note'));
  } else node.append(element('strong', 'Unavailable'));
  return node;
}
function sourceBadge(text, warning = false) { return element('span', text, warning ? 'source-badge warning' : 'source-badge'); }
function drawCards() {
  const matches = filterFacilities(records, route), lastId = history.state?.atlas?.lastId;
  const items = matches.map(record => {
    const item = element('li'), card = button('', () => openFacility(record.id), 'facility-card');
    card.id = `open-${record.id}`; card.setAttribute('aria-label', `Explore ${record.name}`);
    const copy = element('span', undefined, 'card-copy'), identity = element('span', record.id, 'card-id');
    if (lastId === record.id) identity.append(element('span', 'Last viewed'));
    copy.append(identity, element('span', record.name, 'card-heading'), element('span', record.typeLabel, 'card-type'), element('span', 'Explore facility →', 'card-open'));
    card.append(image(record), copy); item.append(card); return item;
  });
  $('facilities').replaceChildren(...items); $('result-count').textContent = `${matches.length} of ${records.length} facilities`;
  $('empty').hidden = matches.length !== 0;
}
function addDefinition(list, label, value) { list.append(element('dt', label), element('dd', value)); }
function facilityDomainNav(domain) {
  const nav = element('nav', undefined, 'domain-nav');
  for (const item of DOMAINS) {
    const control = button(item.toUpperCase(), () => { route.domain = item; route.metric = ''; history.pushState(history.state, '', routeHash(route)); drawDetail(); });
    control.classList.toggle('selected', domain === item); nav.append(control);
  }
  return nav;
}
function drawDetail() {
  const view = $('detail-view'), back = button('← Back', backToList, 'back secondary'); back.id = 'back-to-list';
  if (route.institutionId) { drawInstitution(view, back); return; }
  if (!route.facilityId) { drawBody(view); return; }
  const record = findFacility(records, route.facilityId), title = element('h1', record?.name || 'Facility not found');
  title.id = 'detail-title'; title.tabIndex = -1;
  if (!record) { view.replaceChildren(back, title, element('p', `No facility matches “${route.facilityId}” in the live Ceres identity set.`)); return; }
  const facility = atlasData.facilities[record.id], data = facilityData(record.id);
  const domain = DOMAINS.includes(route.domain) ? route.domain : 'people';
  const heading = element('div', '', 'detail-heading');
  heading.append(element('p', `CERES / ${record.id}`, 'eyebrow'), title, element('p', `${record.typeLabel} · ${facility.identity.traffic || 'Traffic unavailable'}`, 'lede'));
  const figure = element('figure', undefined, 'detail-media'); figure.append(image(record, true), element('figcaption', 'HERO · Approved reference imagery'));
  const retry = button('Retry image', () => { figure.replaceChild(image(record, true), figure.firstChild); }, 'secondary'); retry.setAttribute('aria-label', 'Retry facility image');
  const analysis = element('section', undefined, 'analysis'); analysis.setAttribute('aria-live', 'polite'); analysis.append(element('p', domain.toUpperCase(), 'eyebrow'));
  const grid = element('div', undefined, 'analysis-grid');
  if (domain === 'people') grid.append(
    metric('Resident population', whole(data.residents), 'Facility residents; separate from workforce and transients'),
    metric('Daily transients', whole(data.transients), 'NULL remains unavailable; never converted to zero'),
    metric('Workforce', whole(data.workforce), 'Facility workforce measure'),
    metric('Habitable capacity', finite(data.capacity) ? `${whole(data.capacity)} eq.` : 'Unavailable', 'Capacity is not population'));
  if (domain === 'economy') grid.append(
    metric('Annual value added', scaled(data.output, 1e9, ' B / year', 2), 'Annual flow'),
    metric('Annual operating cost', scaled(data.cost, 1e9, ' B / year', 2), 'Annual flow'),
    metric('Capital stock', scaled(data.capital, 1e12, ' T', 3), 'Accumulated stock'),
    metric('Replacement value', scaled(data.replacement, 1e12, ' T', 3), 'Accumulated value'));
  if (domain === 'transit') grid.append(
    metric('Cargo throughput', scaled(data.cargo, 1e6, ' M tonnes / year', 3)),
    metric('Passenger movements', scaled(data.passengers, 1e6, ' M / year', 3)), metric('Ship calls', finite(data.calls) ? `${decimal(data.calls, 2)} / year` : 'Unavailable'),
    metric('Origin–destination corridors', 'Unavailable', 'Endpoint and aggregation validation pending'));
  if (domain === 'infrastructure') grid.append(metric('Average power', finite(data.average) ? `${whole(data.average)} MW` : 'Unavailable'), metric('Peak power', finite(data.peak) ? `${whole(data.peak)} MW` : 'Unavailable'),
    metric('Habitable capacity', finite(data.capacity) ? `${whole(data.capacity)} eq.` : 'Unavailable', 'Capacity is distinct from utilization'), metric('Utilization', decimal(data.utilization)), metric('Industrial capacity index', decimal(data.industrial)));
  if (domain === 'institutions') {
    for (const relation of facility.institutions) grid.append(metricNode(relation.relationship, relation));
    if (!facility.institutions.length) grid.append(metric('Institutional relationships', 'Unavailable'));
  }
  if (domain === 'society') {
    for (const [label, key] of Object.values(SOCIETY_METRICS)) grid.append(metric(label, decimal(data[key])));
    for (const pressure of facility.social_pressures) grid.append(metric(pressure.pressure_type.replaceAll('_', ' '), decimal(pressure.intensity), `${pressure.direction} · ${pressure.affected_groups}`));
  }
  const grain = facility.infrastructure?.node_subject_id || facility.social?.subject_id || facility.subject_id;
  analysis.append(grid, element('p', `CIVSTATE · ${grain} · ${yearOf(facility.infrastructure || facility.social)}. Source NULL remains unavailable; zero remains numeric zero.`, 'source-note'));
  const facts = element('dl', undefined, 'facts');
  for (const [label, value] of [['Facility ID', record.id], ['Facility type', record.typeLabel], ['WORLD source', facility.identity.source || 'Unavailable'], ['Civil authority (identity field)', facility.identity.civil_authority || 'Unavailable'], ['CIVSTATE governance style', facility.runtime_context?.governance_style || 'Unavailable']]) {
    const group = element('div'); addDefinition(group, label, value); facts.append(group);
  }
  const provenance = element('details', undefined, 'provenance'), defs = element('dl');
  for (const [label, value] of [['WORLD row', `infrastructure_nodes.node_id=${record.id}`], ['CIVSTATE row', `civ_infrastructure_state.node_subject_id=${facility.subject_id}; year=${yearOf(facility.infrastructure)}`], ['Manifest', 'docs/ceres/manifest.json'], ['Manifest SHA-256', sourceHash], ['Knowledge noun ID', record.nounId], ['Asset ID', record.assetId], ['Media key', record.mediaKey], ['Review status', record.review], ['Image SHA-256', record.hash], ['Image bytes', String(record.bytes)]]) addDefinition(defs, label, value);
  provenance.append(element('summary', 'Evidence & image provenance'), defs);
  view.replaceChildren(back, heading, figure, retry, facilityDomainNav(domain), analysis, facts, provenance); document.title = `${record.name} · Ceres Atlas`;
}
function bodySubnav(items, selected) {
  const nav = element('div', undefined, 'subnav');
  for (const item of items) {
    const [key, label] = Array.isArray(item) ? item : [item.toLowerCase().replace(/[^a-z]+/g, '-'), item], active = key === selected;
    const control = button(label, () => { route.metric = key; history.pushState(history.state, '', routeHash(route)); drawBody($('detail-view')); }, active ? 'selected' : '');
    control.setAttribute('aria-pressed', String(active)); nav.append(control);
  }
  return nav;
}
function metricBar(label, value, width) {
  const row = element('div', undefined, 'bar-row'), bar = element('span', undefined, 'bar'), fill = element('i');
  fill.style.width = `${finite(width) ? Math.max(0, Math.min(100, width)) : 0}%`; bar.append(fill); row.append(element('span', label), bar, element('strong', value)); return row;
}
function facilityComparisons(key, format, domain, secondKey = null) {
  const wrap = element('div', undefined, 'comparisons');
  const candidates = records.flatMap(record => { const data = facilityData(record.id); return [data[key], secondKey ? data[secondKey] : null].filter(finite); });
  const max = candidates.length ? Math.max(...candidates) : null;
  for (const record of records) {
    const data = facilityData(record.id), value = data[key], second = secondKey ? data[secondKey] : undefined;
    const row = button('', () => openFacility(record.id), 'comparison-row'); row.setAttribute('aria-label', `Open ${record.name} dossier on ${domain}`);
    const top = element('span', undefined, 'comparison-label'); top.append(element('span', data.short), element('strong', finite(value) ? format(value, second) : 'Unavailable'));
    const track = element('span', undefined, 'comparison-track'), fill = element('i');
    fill.style.width = finite(value) && finite(max) && max > 0 ? `${(value / max) * 100}%` : '0%'; track.append(fill); row.append(top, track);
    if (secondKey) {
      const track2 = element('span', undefined, 'comparison-track light'), fill2 = element('i');
      fill2.style.width = finite(second) && finite(max) && max > 0 ? `${(second / max) * 100}%` : '0%'; track2.append(fill2); row.append(track2);
    }
    wrap.append(row);
  }
  return wrap;
}
function topologySection() {
  const schematic = element('section', undefined, 'topology'), heading = element('div', undefined, 'section-heading');
  heading.append(element('div', undefined), sourceBadge('SCHEMATIC')); heading.firstChild.append(element('p', 'INTERACTIVE SPATIAL INDEX', 'eyebrow'), element('h2', 'Ceres network')); schematic.append(heading);
  const diagram = element('div', undefined, 'topology-diagram'); diagram.setAttribute('role', 'group'); diagram.setAttribute('aria-label', 'Ceres-centered facility topology'); diagram.append(element('span', 'CERES', 'topology-center'));
  const points = [['CER-P01', 'Occator', 'topology-p1'], ['CER-P02', 'Polar Terminal', 'topology-p2'], ['CER-P03', 'Belt Exchange', 'topology-p3'], ['CER-P04', 'Shipyard Arc', 'topology-p4'], ['CER-P05', 'Metric Anchorage*', 'topology-p5']];
  for (const [id, label, className] of points) {
    const record = findFacility(records, id), control = button(label, () => openFacility(id), `topology-node ${className}`);
    control.id = `topology-${id}`; control.setAttribute('aria-label', `${record?.name || label} facility`); diagram.append(control);
  }
  schematic.append(diagram, element('p', 'Relationship schematic · not physical orbital distance. Metric Anchorage placement remains unverified.', 'source-note')); return schematic;
}
function sectionHeading(title, badge, warning = false) { const head = element('div', undefined, 'section-heading'); head.append(element('h2', title), sourceBadge(badge, warning)); return head; }
function factRow(label, value) { const row = element('div', undefined, 'fact-row'); row.append(element('span', label), element('strong', value)); return row; }
function unsupported(section, title, detail) { section.append(element('h3', title), metric('Source status', 'Unavailable'), element('p', detail, 'source-note')); }
function drawWorld(section, selected) {
  const world = atlasData.world;
  section.append(sectionHeading('The world', 'WORLD SQL'), bodySubnav([['environment', 'Environment'], ['resources', 'Resources'], ['history', '2026 history']], selected));
  if (selected === 'resources') { unsupported(section, 'Resources', 'No approved runtime WORLD resource projection is available for this Atlas view.'); return; }
  if (selected === 'history') { unsupported(section, 'Historical observation through 2026', 'No approved runtime WORLD historical-observation projection is available for this Atlas view.'); return; }
  section.append(element('h3', 'Physical conditions'));
  const facts = element('div', undefined, 'world-facts'), radius = world?.mean_radius_km, gm = world?.gm_km3_s2;
  const gravity = finite(radius) && finite(gm) ? gm / (radius * radius) * 1000 : null, escape = finite(radius) && finite(gm) ? Math.sqrt(2 * gm / radius) : null;
  const rotationHours = finite(world?.rotation_period_s) ? world.rotation_period_s / 3600 : null;
  for (const [label, value, note] of [['Diameter', finite(radius) ? `${(radius * 2).toFixed(1)} km` : 'Unavailable', 'Derived: 2 × mean radius'], ['Surface gravity', finite(gravity) ? `${gravity.toFixed(3)} m/s²` : 'Unavailable', 'Derived from GM and mean radius'], ['Escape speed', finite(escape) ? `${escape.toFixed(3)} km/s` : 'Unavailable', 'Derived; not mission Δv'], ['Rotation', finite(rotationHours) ? `${rotationHours.toFixed(2)} hours` : 'Unavailable', 'WORLD rotation period']]) {
    const card = element('div'); card.append(element('span', label), element('strong', value), element('small', note)); facts.append(card);
  }
  section.append(facts, element('h3', 'Atmosphere'), metric('WORLD atmosphere class', world?.atmosphere_class || 'Unavailable'), element('p', `WORLD entities/celestial_properties/celestial_dynamics · ${world?.physical_source_id || 'source unavailable'} · ${world?.physical_status || 'status unavailable'}. Derived values are identified above.`, 'source-note'));
}
function drawPeople(section, selected) {
  const demographic = atlasData.body.demographic, bio = demographic?.biological_population, synth = demographic?.synthetic_population;
  const combined = finite(bio) && finite(synth) ? bio + synth : null;
  section.append(sectionHeading('People and settlement', 'CIVSTATE SQL'), bodySubnav([['composition', 'Composition'], ['age', 'Age'], ['facilities', 'Facilities'], ['zones', 'Zones']], selected));
  if (selected === 'age') {
    section.append(element('p', `BODY · AGE INVENTORY · ${yearOf(demographic)}`, 'eyebrow'), factRow('Age 0–14', whole(demographic?.age_0_14)), factRow('Age 15–64', whole(demographic?.age_15_64)), factRow('Age 65+', whole(demographic?.age_65_plus)), factRow('Age 80+', whole(demographic?.age_80_plus)), factRow('Median age', finite(demographic?.median_age) ? `${decimal(demographic.median_age, 1)} years` : 'Unavailable'), element('p', 'Age denominators overlap or remain unresolved in the source contract; these source fields are not converted into a partition or percentages.', 'source-note')); return;
  }
  if (selected === 'facilities') { section.append(element('h3', 'Facility residents'), facilityComparisons('residents', whole, 'People'), element('p', 'Facility resident, transient, workforce and capacity fields remain distinct in each dossier.', 'source-note')); return; }
  if (selected === 'zones') {
    section.append(element('p', 'CENSUS ZONES · 2226', 'eyebrow'));
    for (const zone of atlasData.zones) section.append(factRow(zone.display_name, `${whole(zone.biological_population)} biological · ${whole(zone.synthetic_population)} synthetic`));
    section.append(element('p', 'Zone-to-node relations are retained separately. Zone totals are not substituted for facility populations; reconciliation remains unresolved.', 'source-note')); return;
  }
  section.append(element('p', `BODY · RECOGNIZED RESIDENTS · ${yearOf(demographic)}`, 'eyebrow'), element('h3', finite(combined) ? scaled(combined, 1e6, ' million', 3) : 'Unavailable'));
  if (finite(combined) && combined > 0 && finite(bio) && finite(synth)) {
    const stack = element('div', undefined, 'population-stack'), bioPart = element('span', `${(bio / combined * 100).toFixed(1)}%`, 'bio'), synthPart = element('span', `${(synth / combined * 100).toFixed(1)}%`, 'synthetic'); bioPart.style.width = `${bio / combined * 100}%`; synthPart.style.width = `${synth / combined * 100}%`; stack.append(bioPart, synthPart);
    const counts = element('div', undefined, 'population-counts'); counts.append(metric('BIOLOGICAL', whole(bio)), metric('SYNTHETIC', whole(synth))); section.append(stack, counts);
  } else section.append(metric('Population composition', 'Unavailable'));
  section.append(factRow('Body-level transient measure', present(demographic?.transient_population) ? whole(demographic.transient_population) : 'Unavailable (source NULL)'), element('p', 'Biological and synthetic residents are combined only within the same BODY row and epoch. Transients remain separate.', 'source-note'));
}
function drawEconomy(section, selected) {
  const economy = atlasData.body.economy;
  section.append(sectionHeading('The economy', 'CIVSTATE SQL'), element('p', `BODY LEVEL · ${yearOf(economy)} · MODEL MONETARY UNIT`, 'eyebrow'), element('h3', scaled(economy?.value_added, 1e12, ' T / year', 3)), element('p', 'Annual value added'), bodySubnav([['output', 'Output'], ['capital', 'Capital'], ['cost', 'Op. cost']], selected));
  if (selected === 'output') {
    const output = economy?.value_added, investment = economy?.investment;
    const ratio = finite(output) && output !== 0 && finite(investment) ? investment / output * 100 : null;
    section.append(element('h3', 'Annual flows · common scale'), metricBar('Value added', scaled(output, 1e12, ' T / yr', 3), 100), metricBar('Investment', scaled(investment, 1e12, ' T / yr', 3), ratio), element('p', 'Production and investment are separate annual flows. Monetary-unit definition remains qualified.', 'source-note'));
  }
  section.append(element('h3', 'Capital and economic indicators'), factRow('Productive capital', scaled(economy?.productive_capital, 1e12, ' T', 3)), factRow('Infrastructure capital', scaled(economy?.infrastructure_capital, 1e12, ' T', 3)), factRow('Capital / annual output', decimal(economy?.capital_output_ratio)), factRow('Investment / annual output', decimal(economy?.investment_output_ratio)), factRow('Income per capita', whole(economy?.income_per_capita)), factRow('Productivity index', decimal(economy?.productivity_index)), element('h3', 'Facility economic comparisons'), selected === 'capital' ? facilityComparisons('capital', value => scaled(value, 1e12, ' T', 3), 'Economy') : selected === 'cost' ? facilityComparisons('cost', value => scaled(value, 1e9, ' B / year', 2), 'Economy') : facilityComparisons('output', value => scaled(value, 1e9, ' B / year', 2), 'Economy'));
}
function drawTransit(section, selected) {
  section.append(sectionHeading('Movement and exchange', 'CIVSTATE NODE SQL'), element('p', 'Each row opens the shared facility dossier on Transit.'), bodySubnav([['cargo', 'Cargo'], ['passengers', 'Passengers'], ['calls', 'Ship calls']], selected), selected === 'passengers' ? facilityComparisons('passengers', value => scaled(value, 1e6, ' M / year', 3), 'Transit') : selected === 'calls' ? facilityComparisons('calls', value => `${decimal(value, 2)} / year`, 'Transit') : facilityComparisons('cargo', value => scaled(value, 1e6, ' M tonnes / year', 3), 'Transit'), element('h3', 'Origin–destination network'), sourceBadge('UNAVAILABLE · endpoint validation pending', true), element('p', 'The transport-flow source exists, but corridors remain withheld until typed endpoint and aggregation validation is complete.', 'source-note'));
}
function drawInfrastructure(section, selected) {
  section.append(sectionHeading('Infrastructure', 'CIVSTATE NODE SQL'), bodySubnav([['power', 'Power'], ['capacity', 'Capacity'], ['utilization', 'Utilization'], ['industrial', 'Industrial']], selected), element('h3', selected === 'capacity' ? 'Habitable capacity' : selected === 'utilization' ? 'Utilization index' : selected === 'industrial' ? 'Industrial capacity index' : 'Average and peak demand'), selected === 'capacity' ? facilityComparisons('capacity', value => `${whole(value)} eq.`, 'Infrastructure') : selected === 'utilization' ? facilityComparisons('utilization', value => decimal(value), 'Infrastructure') : selected === 'industrial' ? facilityComparisons('industrial', value => decimal(value), 'Infrastructure') : facilityComparisons('peak', (peak, average) => `${whole(average)} / ${whole(peak)} MW`, 'Infrastructure', 'average'), element('p', selected === 'power' ? 'Dark bar: peak. Light bar: average. Demand is not a reliability judgment.' : 'Capacity, utilization and industrial capacity retain separate source semantics.', 'source-note'));
}
function drawInstitutions(section, selected) {
  section.append(sectionHeading('Institutions', 'TYPED CIVSTATE EDGES'), bodySubnav([['authority', 'Authority'], ['influence', 'Influence']], selected));
  const civilEdges = Object.values(atlasData.facilities).flatMap(facility => facility.institutions.filter(relation => relation.relationship === 'civil authority'));
  const counts = civilEdges.reduce((result, relation) => result.set(relation.institution_id, (result.get(relation.institution_id) || 0) + 1), new Map());
  const commonId = [...counts].find(([, count]) => count === records.length)?.[0], common = atlasData.institutions[commonId], commonPanel = element('div', undefined, 'institution-common');
  commonPanel.append(element('span', 'DOCUMENTED CIVIL AUTHORITY'), instButton(commonId, 'Unavailable'), element('p', common ? `${common.facilities.length} typed facility relationship records at epoch 2226.` : 'No typed relationship record available.')); section.append(commonPanel);
  for (const record of records) {
    const facility = atlasData.facilities[record.id], card = element('article', undefined, 'governance-card'); card.append(button(record.name, () => openFacility(record.id), 'facility-name'));
    for (const relation of facility.institutions.filter(item => ['GOVERNANCE', 'OPERATIONS', 'SECURITY'].includes(item.domain))) {
      card.append(element('span', relation.relationship.toUpperCase()), instButton(relation.institution_id, relation.name));
      if (selected === 'influence') card.append(element('small', `${relation.control_class} · ${decimal(relation.weight)} influence weight`, 'metric-note'));
    }
    section.append(card);
  }
  section.append(element('p', 'Influence weight describes the modeled relationship. It is not legal authority, equity ownership or revenue control.', 'source-note'));
}
function drawSociety(section, selected) {
  const [label, key] = SOCIETY_METRICS[selected] || SOCIETY_METRICS.trust;
  section.append(sectionHeading('Society', 'CIVSTATE MODEL INDICES', true), element('p', 'Facility-specific fictional model indices; not surveys and not a calculated Ceres-wide average.'), bodySubnav(Object.entries(SOCIETY_METRICS).map(([id, entry]) => [id, entry[0]]), selected), element('h3', label), facilityComparisons(selected, value => decimal(value), 'Society'), element('p', '0 · Index minimum                                      1 · Index maximum', 'scale-note'));
  const pressureCount = Object.values(atlasData.facilities).reduce((total, facility) => total + facility.social_pressures.length, 0);
  section.append(element('h3', 'Separate social-pressure inventory'), element('p', `${pressureCount} source-backed facility pressure records are available in the five dossiers.`), element('p', `Selected source field: civ_social_state.${key}. Pressure records come from civ_social_pressure.`, 'source-note'));
}
function drawBody(view) {
  const domain = BODY_DOMAINS.includes(route.domain) ? route.domain : 'world';
  const defaults = {world: 'environment', people: 'composition', economy: 'output', transit: 'cargo', infrastructure: 'power', institutions: 'authority', society: 'trust'};
  const selected = route.metric || defaults[domain], title = element('h1', atlasData.world?.name || 'Ceres identity unavailable'); title.id = 'detail-title'; title.tabIndex = -1;
  const identity = element('section', undefined, 'body-identity'); identity.append(element('p', 'SOL / MAIN BELT / DWARF PLANET', 'eyebrow'));
  if (domain === 'world') {
    const hero = element('figure', undefined, 'hero-ceres'), heroImage = element('img');
    const fallback = element('span', 'Approved Ceres WORLD HERO unavailable. No substitute is shown.', 'image-fallback');
    heroImage.alt = 'Ceres — approved WORLD reference image'; fallback.hidden = true;
    heroImage.addEventListener('error', () => { heroImage.hidden = true; fallback.hidden = false; }); heroImage.addEventListener('load', () => { heroImage.hidden = false; fallback.hidden = true; });
    heroImage.src = 'assets/ceres-world-hero.png'; hero.append(heroImage, fallback, element('figcaption', 'HERO · APPROVED_REFERENCE · asset 0e516224-6345-4e97-b6d1-569bf193f495'));
    identity.append(hero, title, element('p', 'The physical world. The inhabited world.', 'lede'));
  } else { title.className = 'sr-only'; identity.append(title); }
  const demographic = atlasData.body.demographic, economy = atlasData.body.economy;
  const combined = finite(demographic?.biological_population) && finite(demographic?.synthetic_population) ? demographic.biological_population + demographic.synthetic_population : null;
  const headline = element('section', undefined, 'headline-metrics'), grid = element('div', undefined, 'headline-grid');
  for (const [label, value, note] of [['Biological residents', scaled(demographic?.biological_population, 1e6, 'M', 3), `CIVSTATE · ${yearOf(demographic)}`], ['Synthetic residents', scaled(demographic?.synthetic_population, 1e6, 'M', 3), `CIVSTATE · ${yearOf(demographic)}`], ['Combined residents', scaled(combined, 1e6, 'M', 3), 'Same BODY row; biological + synthetic'], ['Annual value added', scaled(economy?.value_added, 1e12, 'T', 3), 'Model monetary units / year'], ['Productive capital', scaled(economy?.productive_capital, 1e12, 'T', 3), 'Model accumulated stock'], ['Facilities in pilot', String(Object.keys(atlasData.facilities).length), 'Verified WORLD identities']]) {
    const card = element('div', undefined, 'headline-kpi'); card.append(element('span', label), element('strong', value), element('small', note)); grid.append(card);
  }
  headline.append(grid);
  const layers = element('section', undefined, 'evidence-layers');
  layers.setAttribute('aria-label', 'Source layers');
  layers.append(element('div', 'NASA/JPL PHYSICAL REFERENCE\nWORLD physical-source fields; distinct from the 2226 model.', 'evidence-layer'),
    element('div', 'HISTORICAL OBSERVATION THROUGH 2026\nUnavailable in the bounded runtime projection.', 'evidence-layer'),
    element('div', 'FICTIONAL LOOM 2226\nCIVSTATE demographics, economy, facilities, institutions and society.', 'evidence-layer'));
  const nav = element('nav', undefined, 'domain-nav'); nav.setAttribute('aria-label', 'Analytical navigation'); nav.append(element('span', 'ANALYTICAL NAVIGATION', 'nav-label'));
  for (const item of BODY_DOMAINS) {
    const control = button(item === 'infrastructure' ? 'Systems' : item[0].toUpperCase() + item.slice(1), () => { route.domain = item; route.metric = ''; route.collection = ''; history.pushState(history.state, '', routeHash(route)); drawBody(view); });
    control.classList.toggle('selected', domain === item); nav.append(control);
  }
  const section = element('section', undefined, 'body-analysis');
  if (domain === 'world') drawWorld(section, selected);
  if (domain === 'people') drawPeople(section, selected);
  if (domain === 'economy') drawEconomy(section, selected);
  if (domain === 'transit') drawTransit(section, selected);
  if (domain === 'infrastructure') drawInfrastructure(section, selected);
  if (domain === 'institutions') drawInstitutions(section, selected);
  if (domain === 'society') drawSociety(section, selected);
  const browse = button('Browse facility collection', () => {
    route = {query: route.query || '', type: route.type || '', facilityId: '', institutionId: '', domain: '', metric: '', collection: '1'};
    history.pushState({atlas: listSnapshot(history.state?.atlas), fromBody: true}, '', routeHash(route)); render();
  }, 'secondary');
  browse.id = 'browse-facility-collection';
  view.replaceChildren(identity, headline, layers, nav, section, browse, topologySection()); document.title = `${domainTitle(domain)} · Ceres Atlas`;
}
function domainTitle(domain) { return ({world: 'Ceres world dossier', people: 'People and settlement', economy: 'The economy', transit: 'Movement and exchange', infrastructure: 'Infrastructure', institutions: 'Institutions', society: 'Society'})[domain] || 'Ceres world dossier'; }
function drawInstitution(view, back) {
  const info = atlasData.institutions[route.institutionId], title = element('h1', info ? (info.name || 'Institution identity unavailable') : 'Institution not found'); title.id = 'detail-title'; title.tabIndex = -1;
  if (!info) { view.replaceChildren(back, title, element('p', 'No typed institution relationship matches this route.')); return; }
  const body = element('div', undefined, 'analysis');
  body.append(element('p', `INSTITUTION / ${info.institution_class}`, 'eyebrow'), element('p', `Typed identity ${info.id} · epoch ${atlasData.epoch}`, 'lede'), element('p', 'Relationship types and influence weights come from CIVSTATE typed influence edges. They do not imply equity ownership or sovereign authority beyond each named relationship.', 'source-note'));
  const list = element('div', undefined, 'analysis-grid');
  for (const relation of info.facilities) {
    const record = findFacility(records, relation.facility_id); if (!record) continue;
    const card = element('div', undefined, 'metric'), control = button(record.name, () => openFacility(record.id), 'entity-link'); control.setAttribute('aria-label', `Open linked facility: ${record.name}`);
    card.append(element('span', `${relation.relationship} · ${relation.domain}`), control, element('small', `${relation.control_class} · influence ${decimal(relation.weight)} · ${relation.derivation_id}`, 'metric-note')); list.append(card);
  }
  if (!list.children.length) list.append(metric('Linked facilities', 'Unavailable'));
  body.append(list, element('p', `CIVSTATE civ_subject + v_graph_civstate_influence_edges · ${info.navigator_noun_id || 'Navigator noun unavailable'}.`, 'source-note'));
  view.replaceChildren(back, title, body); document.title = `${title.textContent} · Ceres Atlas`;
}
function render() {
  if (!ready) return;
  route = parseRoute(location.hash); renderedHash = location.hash; const version = ++renderVersion, detail = !route.collection;
  $('list-view').hidden = detail; $('detail-view').hidden = !detail;
  if (detail) { drawDetail(); window.scrollTo(0, 0); $('detail-title').focus({preventScroll: true}); }
  else {
    $('search').value = route.query; document.querySelector('option[data-unknown]')?.remove();
    if (route.type && !records.some(record => record.type === route.type)) { const option = element('option', `Unknown type: ${route.type}`); option.value = route.type; option.dataset.unknown = 'true'; $('type-filter').append(option); }
    $('type-filter').value = route.type; drawCards(); document.title = 'Ceres Atlas · LOOM 2226'; const snapshot = listSnapshot(history.state?.atlas);
    requestAnimationFrame(() => { if (version !== renderVersion) return; ($(snapshot.focus) || $('list-title')).focus({preventScroll: true}); window.scrollTo(0, snapshot.scroll); });
  }
}
function filterChanged() {
  route = {query: $('search').value, type: $('type-filter').value, facilityId: '', institutionId: '', domain: '', collection: '1'};
  saveList(); renderedHash = location.hash; drawCards();
}
async function load() {
  ready = false; $('loading').hidden = false; $('load-error').hidden = true;
  try {
    const [manifestResponse, dataResponse] = await Promise.all([fetch('manifest.json', {cache: 'no-store'}), fetch('atlas-data.json', {cache: 'no-store'})]);
    if (!manifestResponse.ok) throw new Error('The local manifest is unavailable.');
    if (!dataResponse.ok) throw new Error('The WORLD or CIVSTATE data is unavailable.');
    const [manifest, data] = await Promise.all([manifestResponse.json(), dataResponse.json()]);
    if (data?.schema_version !== 1 || data?.epoch !== 2226 || data?.world?.entity_id !== 'CER' || !data.facilities || Object.keys(data.facilities).length !== 5 || !data.institutions) throw new Error('The runtime Atlas data has an unsupported format.');
    atlasData = data;
    records = validateManifest(manifest).map(record => {
      const identity = data.facilities[record.id]?.identity;
      if (!identity || identity.node_id !== record.id || identity.facility_type !== record.type) throw new Error('WORLD and approved media identities do not agree.');
      return Object.freeze({...record, name: identity.node_name, type: identity.facility_type, typeLabel: typeLabel(identity.facility_type)});
    });
    sourceHash = manifest.source_sha256;
    const options = [...new Set(records.map(record => record.type))].map(type => { const option = element('option', records.find(record => record.type === type).typeLabel); option.value = type; return option; });
    const all = element('option', 'All types'); all.value = ''; $('type-filter').replaceChildren(all, ...options);
    ready = true; $('loading').hidden = true; render();
  } catch (error) {
    $('loading').hidden = true; $('load-error').hidden = false;
    $('error-message').textContent = `Keep the Ceres Atlas launcher running with readable WORLD and CIVSTATE databases and the approved manifest, then try again. ${error.message}`; $('error-title').focus();
  }
}
$('search').addEventListener('input', filterChanged);
$('type-filter').addEventListener('change', filterChanged);
$('clear-filters').addEventListener('click', () => { $('search').value = ''; $('type-filter').value = ''; filterChanged(); $('search').focus(); saveList(); });
$('retry-load').addEventListener('click', load);
document.querySelector('.skip-link').addEventListener('click', event => { event.preventDefault(); $('main').focus(); });
document.addEventListener('keydown', event => { if (ready && (route.facilityId || route.institutionId) && event.key === 'Escape' && !event.defaultPrevented) { event.preventDefault(); backToList(); } });
for (const name of ['popstate', 'hashchange']) window.addEventListener(name, () => { if (location.hash !== renderedHash) render(); });
window.addEventListener('pagehide', () => { if (ready && !route.facilityId && !route.institutionId) saveList(); });
load();
