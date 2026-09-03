(() => {
'use strict';

function destinationFromPanel() {
  const el = document.querySelector('#flightPlanningPanel .fpDestination');
  const text = String(el?.textContent || '').trim().toUpperCase();
  if (!text || text === 'SELECT ON MAP' || text === '—') return null;
  return text;
}

function installPixelNavigationShim() {
  document.addEventListener('click', (event) => {
    const button = event.target && event.target.closest ? event.target.closest('#flightPlanningPanel .fpDiscover') : null;
    if (!button) return;

    const label = String(button.textContent || '').trim().toUpperCase();
    if (!label.startsWith('DISCOVER ROUTES')) return;

    const destination = destinationFromPanel();
    if (!destination) return;

    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    button.disabled = true;
    button.textContent = `OPENING ROUTE SEARCH · ${destination}`;
    const status = document.querySelector('#flightPlanningPanel .fpStatus');
    if (status) status.textContent = `STARTING NAVIGATOR · ${destination}`;

    const q = new URLSearchParams({destination, priority: 'BALANCED', ts: String(Date.now())});
    window.location.assign('/flight-planning/discover-start?' + q.toString());
  }, true);

  const params = new URLSearchParams(window.location.search);
  const jobId = params.get('fp_job');
  if (!jobId) return;

  const destination = params.get('fp_destination') || '';
  const cleanUrl = window.location.pathname;
  history.replaceState(null, '', cleanUrl);

  const waitForPlanner = () => {
    const panel = document.getElementById('flightPlanningPanel');
    if (!panel) {
      setTimeout(waitForPlanner, 100);
      return;
    }
    const status = panel.querySelector('.fpStatus');
    if (status) status.textContent = `DISCOVERING ROUTES · ${destination || 'DESTINATION'}`;

    let attempts = 0;
    const poll = async () => {
      attempts += 1;
      try {
        const response = await fetch('/flight-planning/status.json?ts=' + Date.now(), {cache: 'no-store'});
        if (!response.ok) throw new Error(`STATUS HTTP ${response.status}`);
        const data = await response.json();
        if (data.job_id !== jobId) {
          if (attempts < 180) return setTimeout(poll, 1000);
          throw new Error('route discovery job was replaced');
        }
        if (data.status === 'RUNNING') {
          if (status) status.textContent = `DISCOVERING ROUTES · ${destination || 'DESTINATION'} · ${attempts}s`;
          if (attempts < 180) return setTimeout(poll, 1000);
          throw new Error('route discovery timed out');
        }
        if (data.status === 'ERROR') throw new Error(data.error || 'Navigator discovery failed');
        if (data.status === 'COMPLETE') {
          window.location.reload();
          return;
        }
        if (attempts < 180) return setTimeout(poll, 1000);
        throw new Error('route discovery did not complete');
      } catch (err) {
        if (status) status.textContent = `ERROR · ${String(err?.message || err)}`;
      }
    };
    poll();
  };
  waitForPlanner();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', installPixelNavigationShim, {once: true});
} else {
  installPixelNavigationShim();
}
})();
