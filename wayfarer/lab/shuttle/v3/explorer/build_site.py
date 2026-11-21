"""Write site/data.json from explorer_results.json. ALL bodies. ALL sponsors. 2026-2226."""
import json, site_rows as SR
D = json.load(open('explorer_results.json'))
caps = list(next(r for r in D['results'] if 'capabilities' in r)['capabilities'].keys())
rows = [SR.row(r, full=bool(r['feasible']) or r['id'] in {a['id'] for a in D['archetypes']}) for r in D['results'] if 'dry_t' in r]
cav = next((r.get('caveats') for r in D['results'] if r.get('caveats')), [])
kst = next((r.get('kit_status') for r in D['results'] if r.get('kit_status')), {})
for o in rows: o.pop('cv', None); o.pop('ks', None)
space = dict(D['space']); space['length'] = [12.8, 16.8]; space['wildcard'] = ['none', 'osteon_cautious', 'osteon_airframe', 'osteon_optimistic', 'dense_power', 'high_lift']
out = dict(caveats=cav, kit_status=kst, names=SR.NAMES, masskeys=SR.MASSKEYS, model_version=D['model_version'], metrics=SR.METRICS, params=SR.PARAMS, caps=caps, space=space, archetypes=D['archetypes'],
           pareto_objectives=D['pareto_objectives'], gate_sources={g['name']: g['source'] for r in D['results'] if r.get('gates') for g in r['gates'] + r['capability_margins']}, thresholds=D['thresholds'], evidence=D['evidence_classes'], missions=D['missions'], rows=rows)
s = json.dumps(out, separators=(',', ':')); open('site/data.json', 'w').write(s); print(len(s) / 1e6, 'MB', len(rows))
# copy the model sources the page runs in the browser (Pyodide) as .txt files
import shutil, os
S = os.path.join('..', '..'); os.makedirs('site/py', exist_ok=True)
for f in [os.path.join(S, 'shuttle_inputs.json')] + [os.path.join(S, 'v2_lifting_body', n) for n in ('aero_test.py', 'build_v2b.py', 'variants.py', 'b4s_mass.json')] + \
         [os.path.join(S, 'v3', 'step2_propulsion.py'), 'engine.py', 'missions.py', 'missions.json', 'site_rows.py']:
    shutil.copy(f, os.path.join('site', 'py', os.path.basename(f) + '.txt'))
