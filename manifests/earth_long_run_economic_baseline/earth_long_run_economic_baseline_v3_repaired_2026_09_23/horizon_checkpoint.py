"""Explicit h1 model contract over the unchanged c1 format-1 codec."""
import checkpoint_io as codec

MODEL='v0.6.1-d1-c1-h1-r1-alpha060-national-gfcf1'
SCENARIO={
    'version':'WPP2024_MEDIUM_DECAYING_TAIL_TO_2226_v1',
    'empirical_projection_end_year':2100,
    'previous_authored_tail_end_year':2190,
    'authored_tail_end_year':2226,
    'tail_anchor_transition_end_years':list(range(2092,2101)),
    'population_growth_half_life_years':40.0,
    'working_age_share_delta_half_life_years':30.0,
    'working_age_share_bounds':[0.20,0.80],
    'interpretation':'Authored scenario extension; not an empirical projection; no birth/death/migration ledger',
    'rule':'Continue original annual recurrence with elapsed years measured from 2100; no resetting or terminal-value repetition',
}


def compatibility(namespace,runner):
    compat,constants=codec.compatibility(namespace,runner)
    compat.update(model_version=MODEL,horizon_adapter_sha256=codec.sha(__file__),demographic_scenario=SCENARIO)
    return compat,constants


def load(path,compat,constants):
    # No acceptance or reinterpretation of c1 here. Use the explicit migration.
    return codec.load(path,compat,constants)


def inherit_provenance(compat,manifest):
    if 'horizon_migration' in manifest:
        return dict(compat,horizon_migration=manifest['horizon_migration'])
    return compat


def save(path,year,local_state,compat,constants,input_hashes):
    return codec.save(path,year,local_state,compat,constants,input_hashes)


sha=codec.sha
