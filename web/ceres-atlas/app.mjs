import {validateManifest, parseRoute, routeHash, filterFacilities, findFacility, listSnapshot} from './model.mjs';

const $ = id => document.getElementById(id);
let records = [], route = parseRoute(location.hash), ready = false, renderVersion = 0;
let sourceHash = '', renderedHash = null;
history.scrollRestoration = 'manual';

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
  const view = $('detail-view');
  const back = button('← Back to facilities', backToList, 'back secondary');
  back.id = 'back-to-list';
  const record = findFacility(records, route.facilityId);
  const title = element('h1', record?.name || 'Facility not found');
  title.id = 'detail-title'; title.tabIndex = -1;
  if (!record) {
    view.replaceChildren(back, title, element('p', `No facility matches “${route.facilityId}” in this local collection.`));
    document.title = 'Facility not found · Ceres Atlas';
    return;
  }
  const heading = element('div', undefined, 'detail-heading');
  heading.append(element('p', `Ceres / ${record.id}`, 'eyebrow'), title, element('p', record.typeLabel, 'lede'));
  const figure = element('figure', undefined, 'detail-media');
  figure.append(image(record, true), element('figcaption', 'HERO · Approved reference imagery'));
  const retry = button('Retry image', () => {
    const fresh = image(record, true);
    figure.replaceChild(fresh, figure.firstChild);
  }, 'secondary');
  // This control is useful even if the initial image succeeds and later becomes unavailable.
  retry.setAttribute('aria-label', 'Retry facility image');
  const facts = element('dl', undefined, 'facts');
  for (const [label, value] of [['Facility ID', record.id], ['Facility type', record.typeLabel]]) {
    const group = element('div'); addDefinition(group, label, value); facts.append(group);
  }
  const provenance = element('details', undefined, 'provenance');
  const definitions = element('dl');
  for (const [label, value] of [
    ['Manifest', 'docs/ceres/manifest.json'], ['Manifest SHA-256', sourceHash],
    ['Knowledge noun ID', record.nounId], ['Asset ID', record.assetId],
    ['Media key', record.mediaKey], ['Review status', record.review],
    ['Image SHA-256', record.hash], ['Image bytes', String(record.bytes)],
    ['Facility type code', record.type],
  ]) addDefinition(definitions, label, value);
  provenance.append(element('summary', 'Identity & image provenance'), definitions);
  view.replaceChildren(back, heading, figure, retry, facts,
    element('p', 'Population, economy and infrastructure measures are not included in this reference slice.', 'muted'), provenance);
  document.title = `${record.name} · Ceres Atlas`;
}

function render() {
  if (!ready) return;
  route = parseRoute(location.hash);
  renderedHash = location.hash;
  const version = ++renderVersion;
  const detail = Boolean(route.facilityId);
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
  route = {query: $('search').value, type: $('type-filter').value, facilityId: ''};
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
