"""Bounded water-bearing block compiler beside Build 6E's named-world adapter.

Research Lab v0.3 supplies authored model inputs, never REAL evidence. Only
World Authority's fixed, admitted science projection can constrain WORLD draws.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal as D, getcontext
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from loom_world_authority import store
from loom_world_authority.etl import SOURCE_SHA, canonical
from simulation.offworld_mvp.phase3b.kernel.offworld_kernel.policy import _comparison_draw

ROOT = Path(__file__).resolve().parent
TABLE = ROOT / 'inputs/SOLAR_HIDDEN_WORLD_WATER_PRIOR_TABLE_v0.1.csv'
POLICY = ROOT / 'inputs/SHARED_GENERATION_POLICY_v0.3.json'
TABLE_SHA = '6c04c8e77b63d5cb66b11fad0e4405cfa8597090d61c8b23ba92f558ecc55106'
POLICY_SHA = 'edd4a3fefba7bb5af7cec724692d956bd5c692e8fe6d4b7018a1bb133b95cda6'
RESEARCH_COMMIT = '52b35dc8ec0df6ee20c8e6be6570c8a595c9b12a'
MODEL = 'SOLAR_WATER_BLOCK_COMPILER_V1'
AUTHORITY = 'LOOM_OFFWORLD_GENERATED_WORLD_V1'
USE = 'OFFWORLD_HIDDEN_WORLD_GENERATION_V1'
PI = D('3.141592653589793238462643383')
AU_KM = D('149597870.7')
JULIAN_YEAR_SECONDS = D('31557600')
UNITS = {'mass':'GEN_KG_V1','length':'GEN_M_V1','volume':'GEN_M3_V1',
         'temperature':'GEN_K_V1','pressure':'GEN_PA_V1',
         'distance':'GEN_AU_V1','fraction':'GEN_FRACTION_V1',
         'angle':'GEN_RAD_V1','area':'GEN_M2_V1','density':'GEN_KG_PER_M3_V1'}


class GenerationBlocked(RuntimeError):
    """Invalid declared input or infeasible physical proposal."""


def _hash(value):
    return sha256(canonical(value)).hexdigest()


def load_inputs():
    table_bytes, policy_bytes = TABLE.read_bytes(), POLICY.read_bytes()
    if sha256(table_bytes).hexdigest()!=TABLE_SHA or sha256(policy_bytes).hexdigest()!=POLICY_SHA:
        raise GenerationBlocked('PINNED_PRIOR_BYTES_CHANGED')
    rows={}
    for row in csv.DictReader(table_bytes.decode('utf8').splitlines()):
        key=row['body_id']
        if key in rows or row['table_content_version']!='0.3' or row['shared_policy_id']!='SOLAR_HIDDEN_WORLD_SHARED_POLICY_v0.3':
            raise GenerationBlocked('PRIOR_ROW_VERSION_OR_IDENTITY')
        if row['material_model_applicability'] in ('SOLID','SOLID_WITH_ATMOSPHERE'):
            for lo,hi in (('fallback_radius_min_km','fallback_radius_max_km'),
                          ('fallback_heliocentric_distance_min_au','fallback_heliocentric_distance_max_au')):
                a,b=D(row[lo]),D(row[hi])
                if not a.is_finite() or not b.is_finite() or not 0<a<=b:
                    raise GenerationBlocked('PRIOR_FALLBACK_BOUNDS:'+key)
            weights=[D(row[k]) for k in ('dry_weight','bound_water_weight','free_ice_weight')]
            if any(not w.is_finite() or w<0 for w in weights) or sum(weights)<=0:
                raise GenerationBlocked('PRIOR_BRANCH_WEIGHTS:'+key)
        rows[key]=row
    if len(rows)!=95:raise GenerationBlocked('PRIOR_POPULATION_DRIFT')
    policy=json.loads(policy_bytes)
    if policy['policy_id']!='SOLAR_HIDDEN_WORLD_SHARED_POLICY_v0.3' or policy['scope']['branch_scope']!='PROSPECTING_BLOCK':
        raise GenerationBlocked('SHARED_POLICY_PROFILE')
    return rows,policy


def _draw(seed,body,domain,property_key,attempt=0):
    if getcontext().prec!=28 or str(getcontext().rounding)!='ROUND_HALF_EVEN':
        raise GenerationBlocked('DECIMAL_REPLAY_ENVIRONMENT')
    return _comparison_draw([MODEL,'WORLD',seed,body,domain,'BLOCK_1',property_key,attempt])


def _interval(seed,body,domain,name,lo,hi,attempt,distribution='LINEAR_UNIFORM'):
    lo,hi=D(str(lo)),D(str(hi))
    if not (lo.is_finite() and hi.is_finite() and lo<=hi):raise GenerationBlocked('INVALID_PRIOR_INTERVAL:'+name)
    u=_draw(seed,body,domain,name,attempt)
    if distribution=='LINEAR_UNIFORM':return lo+(hi-lo)*u
    if distribution=='LOG_UNIFORM' and lo>0:return (lo.ln()+(hi.ln()-lo.ln())*u).exp()
    raise GenerationBlocked('INVALID_PRIOR_DISTRIBUTION:'+name)


def _source_range(assertion, unit):
    """Interpret only explicit numeric intervals; no unstated error model."""
    lex=assertion.get('unit_lexeme')
    scale={'kg':D(1),'10^18 kg':D('1e18'),'10^24 kg':D('1e24'),
           'km':D(1000),'m':D(1),'g/cm3':D(1000),'g/cm^3':D(1000),'kg/m3':D(1)}.get(lex)
    expected={'mass':{'kg','10^18 kg','10^24 kg'},'radius':{'km','m'},
              'density':{'g/cm3','g/cm^3','kg/m3'}}[unit]
    if lex not in expected or scale is None:raise GenerationBlocked('UNSUPPORTED_ADMITTED_PHYSICAL_UNIT')
    if assertion['value_kind']=='RANGE' and assertion['value_min'] is not None and assertion['value_max'] is not None:
        return D(assertion['value_min'])*scale,D(assertion['value_max'])*scale
    if assertion['value_kind']=='NUMERIC' and assertion['value_numeric'] is not None and assertion['uncertainty_numeric'] is not None:
        nominal,error=D(assertion['value_numeric']),D(assertion['uncertainty_numeric'])
        return (nominal-error)*scale,(nominal+error)*scale
    # A nominal measurement without an uncertainty model is retained in
    # provenance; treating it as an exact physical equality would launder it.
    return None


def _admitted_range(assertions,kind):
    codes={'mass':{'MASS','DYNAMICAL_MASS'},'radius':{'MEAN_RADIUS','GEOMETRIC_MEAN_DIAMETER','EFFECTIVE_DIAMETER'},
           'density':{'BULK_DENSITY'}}[kind]
    selected=[]
    for a in assertions:
        if a['scope_kind']!='BODY' or a['property_code'] not in codes:continue
        interval=_source_range(a,kind)
        if interval is None:continue
        if a['property_code'] in ('GEOMETRIC_MEAN_DIAMETER','EFFECTIVE_DIAMETER'):
            interval=interval[0]/2,interval[1]/2
        selected.append(interval)
    if not selected:return None
    low,high=max(i[0] for i in selected),min(i[1] for i in selected)
    if not 0<low<=high:raise GenerationBlocked('ADMITTED_BODY_CONSTRAINT_CONFLICT:'+kind)
    return low,high


def _dimensions(row,assertions,seed,body,domain):
    rho_bounds=_admitted_range(assertions,'density') or (
        D(row['latent_body_bulk_density_min_kg_m3']),D(row['latent_body_bulk_density_max_kg_m3']))
    density=_interval(seed,body,domain,'body_bulk_density',*rho_bounds,0,'LOG_UNIFORM')
    mass_bounds=_admitted_range(assertions,'mass')
    radius_bounds=_admitted_range(assertions,'radius')
    if radius_bounds and mass_bounds:
        for attempt in range(64):
            radius=_interval(seed,body,domain,'body_radius',*radius_bounds,attempt,'LOG_UNIFORM')
            volume=D(4)*PI*radius**3/D(3)
            feasible=(max(mass_bounds[0],volume*rho_bounds[0]),
                      min(mass_bounds[1],volume*rho_bounds[1]))
            if feasible[0]<=feasible[1]:
                mass=_interval(seed,body,domain,'body_mass',*feasible,attempt,'LOG_UNIFORM')
                density=mass/volume
                break
        else:raise GenerationBlocked('ADMITTED_MASS_RADIUS_DENSITY_CONFLICT')
    elif radius_bounds:
        radius=_interval(seed,body,domain,'body_radius',*radius_bounds,0,'LOG_UNIFORM')
        mass=D(4)*PI*radius**3*density/D(3)
    elif mass_bounds:
        mass=_interval(seed,body,domain,'body_mass',*mass_bounds,0,'LOG_UNIFORM')
        radius=(D(3)*mass/(D(4)*PI*density))**(D(1)/D(3))
    else:
        radius=_interval(seed,body,domain,'body_radius',D(row['fallback_radius_min_km'])*1000,
            D(row['fallback_radius_max_km'])*1000,0,'LOG_UNIFORM')
        mass=D(4)*PI*radius**3*density/D(3)
    if mass<=0 or radius<=0 or density<=0:raise GenerationBlocked('BODY_GEOMETRY')
    return mass,radius,density


def _sublimation_pressure(temperature,policy):
    p=policy['retention']['sublimation_pressure']
    t=max(temperature,D('50'))
    if t>D('273.16'):return None
    theta=t/D('273.16')
    exponent=sum(D(str(c['a']))*theta**D(str(c['b'])) for c in p['coefficients'])/theta
    return D('611.657')*exponent.exp()


def _retention(block,temperature,policy):
    r=policy['retention']
    vapor=_sublimation_pressure(temperature,policy)
    if vapor is None:return False,D(0)
    flux=r['loss_flux'];cover=block['depth_m']
    exposed=vapor*(D(str(flux['molar_mass_h2o_kg_mol']))/(D(2)*PI*D(str(flux['universal_gas_constant_j_mol_k']))*max(temperature,D('50')))).sqrt()
    buried=block['permeability_m2']*vapor**2/(D(str(r['cover']['water_vapor_dynamic_viscosity_pa_s']))*cover*D(str(flux['water_vapor_specific_gas_constant_j_kg_k']))*max(temperature,D('50')))
    loss=min(exposed,buried)*PI*block['radius_m']**2*D(str(r['horizon_years']))*JULIAN_YEAR_SECONDS
    return loss<=D(str(r['maximum_unforced_target_mass_loss_fraction']))*block['target_mass_kg'],loss


def _environment(row,policy,seed,body,domain,r_au):
    r=policy['retention']
    if row['material_model_applicability']=='SOLID_WITH_ATMOSPHERE':
        env=r['atmospheric_regime_latent_envelopes'].get(row['prior_regime'])
        if env is None:raise GenerationBlocked('MISSING_ATMOSPHERIC_ENVELOPE:'+body)
        return (_interval(seed,body,domain,'atmospheric_temperature',*env['temperature_k'],0),
                _interval(seed,body,domain,'atmospheric_pressure',*env['pressure_pa'],0))
    m=r['airless_equilibrium_model']
    albedo_bounds=m['bond_albedo_if_unconstrained']
    emissivity_bounds=m['emissivity_if_unconstrained']
    albedo=_interval(seed,body,domain,'bond_albedo',albedo_bounds['min'],albedo_bounds['max'],0)
    emissivity=_interval(seed,body,domain,'emissivity',emissivity_bounds['min'],emissivity_bounds['max'],0)
    return (((D(1)-albedo)*D(str(m['solar_constant_w_m2']))/(D(4)*emissivity*D(str(m['stefan_boltzmann_w_m2_k4']))*r_au**2))**D('0.25'),D(0))


def _block(row,policy,seed,body,domain,body_mass,radius,r_au):
    temp,pressure=_environment(row,policy,seed,body,domain,r_au)
    for attempt in range(policy['sampling']['max_rejection_attempts_per_property']):
        weights=[D(row[k]) for k in ('dry_weight','bound_water_weight','free_ice_weight')]
        u=_draw(seed,body,domain,'material_branch',attempt)*sum(weights)
        form='DRY_MATRIX' if u<weights[0] else 'MINERAL_BOUND_H2O_OH' if u<weights[0]+weights[1] else 'FREE_ICE'
        fraction=_interval(seed,body,domain,'block_body_mass_fraction',row['block_body_mass_fraction_min'],row['block_body_mass_fraction_max'],attempt,'LOG_UNIFORM')
        host=min(body_mass*fraction,D(row['block_mass_cap_kg']))
        if form=='DRY_MATRIX':
            sub=policy['target_fraction']['DRY_MATRIX']['subbranches']
            zero_weight=D(str(sub['ZERO_TARGET']['weight']))
            trace_weight=D(str(sub['TRACE_H2O_EQ']['weight']))
            if zero_weight<=0 or trace_weight<=0:raise GenerationBlocked('DRY_SUBBRANCH_WEIGHTS')
            if _draw(seed,body,domain,'dry_subbranch',attempt)<zero_weight/(zero_weight+trace_weight):
                grade=D(0);subtype='ZERO_TARGET'
            else:
                grade=_interval(seed,body,domain,'dry_trace_grade',sub['TRACE_H2O_EQ']['min'],row['dry_h2o_eq_max_wtfrac'],attempt)
                subtype='TRACE_H2O_EQ'
        elif form=='MINERAL_BOUND_H2O_OH':
            grade=_interval(seed,body,domain,'bound_grade',row['bound_h2o_eq_min_wtfrac'],row['bound_h2o_eq_max_wtfrac'],attempt)
            subtype='POTENTIAL_H2O_EQUIVALENT'
        else:
            grade=_interval(seed,body,domain,'ice_grade',row['free_ice_h2o_min_wtfrac'],row['free_ice_h2o_max_wtfrac'],attempt)
            subtype='FREE_WATER_ICE'
        if not D(0)<=grade<=D(1) or not D(0)<host<=body_mass:raise GenerationBlocked('MASS_SIMPLEX')
        rule=policy['block_geometry']['block_density_rule'][form]
        if form=='FREE_ICE':dmin,dmax=rule['min_kg_m3'],rule['max_kg_m3']
        else:dmin,dmax=row[rule['range_from_row'][0]],row[rule['range_from_row'][1]]
        density=_interval(seed,body,domain,'block_density',dmin,dmax,attempt,'LOG_UNIFORM')
        volume=host/density
        block_radius=(D(3)*volume/(D(4)*PI))**(D(1)/D(3))
        p=policy['placement']
        depth_fraction=_interval(seed,body,domain,'top_depth_fraction',
            p['unconstrained_top_depth_fraction_of_body_radius']['min'],
            p['unconstrained_top_depth_fraction_of_body_radius']['max'],attempt,'LOG_UNIFORM')
        depth=min(depth_fraction*radius,D(str(p['absolute_top_depth_cap_m'])))
        if depth+D(2)*block_radius>radius:continue
        permeability=_interval(seed,body,domain,'permeability',
            policy['retention']['cover']['intrinsic_permeability_m2_if_unconstrained']['min'],
            policy['retention']['cover']['intrinsic_permeability_m2_if_unconstrained']['max'],attempt,'LOG_UNIFORM')
        block=dict(form=form,subtype=subtype,host_mass_kg=host,target_fraction=grade,
            target_mass_kg=host*grade,density_kg_m3=density,volume_m3=volume,radius_m=block_radius,
            depth_m=depth,permeability_m2=permeability,temperature_k=temp,pressure_pa=pressure,r_au=r_au,
            longitude_rad=D(2)*PI*_draw(seed,body,domain,'longitude',attempt),
            sin_latitude=D(2)*_draw(seed,body,domain,'sin_latitude',attempt)-D(1),
            attempt=attempt)
        if form=='FREE_ICE':
            retained,loss=_retention(block,temp,policy)
            if not retained:continue
            block['retention_loss_kg']=loss
        else:block['retention_loss_kg']=D(0)
        return block
    raise GenerationBlocked('NO_FEASIBLE_PHYSICAL_PROPOSAL:'+body)


def _state(world_id,body_id,location_id,property_code,value,unit,meaning):
    state_id=store.stable_uuid('HIDDEN_STATE',AUTHORITY,str(world_id)+':'+str(location_id)+':'+property_code,'1')
    payload=dict(world_id=str(world_id),body_id=str(body_id),location_id=str(location_id),
        property_code=property_code,value_state='UNKNOWN' if value is None else 'KNOWN',
        numeric_value=None if value is None else str(value),unit_key=unit,model_family_ref=MODEL,
        uncertainty_ref='AUTHORED_PRIOR_V0_3',derivation_ref=meaning)
    return ('wa_world.hidden_state',dict(state_id=state_id,world_id=world_id,body_id=body_id,
        location_id=location_id,property_code=property_code,value_state=payload['value_state'],
        numeric_value=value,text_value=None,unit_key=unit,model_family_ref=MODEL,
        uncertainty_ref='AUTHORED_PRIOR_V0_3',derivation_ref=meaning,
        value_sha256=_hash(payload),original_provenance_lexeme='PR147:'+RESEARCH_COMMIT))


def _uuid(kind,key,version):
    return store.stable_uuid(kind,AUTHORITY,key,version)


def _property_rows():
    known={'R_IN_SITU':('IN_SITU_STOCK','BUILD6E_NAMED_WORLD_V1'),
           'R_ACCESSIBLE':('ACCESSIBLE_STOCK','BUILD6E_NAMED_WORLD_V1'),
           'R_RECOVERABLE':('RECOVERABLE_STOCK','BUILD6E_NAMED_WORLD_V1'),
           'R_RESERVE':('ECONOMIC_RESERVE_UNKNOWN','BUILD6E_NAMED_WORLD_V1'),
           'GEN_BODY_MASS_KG':('HIDDEN_BODY_MASS','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_BODY_RADIUS_M':('HIDDEN_BODY_RADIUS','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_BODY_BULK_DENSITY':('HIDDEN_BODY_BULK_DENSITY','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_BLOCK_HOST_MASS_KG':('FINITE_HOST_MASS','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_BLOCK_DENSITY':('HIDDEN_BLOCK_DENSITY','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_TARGET_FRACTION':('WATER_TARGET_MASS_FRACTION','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_BLOCK_TOP_DEPTH_M':('BLOCK_TOP_DEPTH','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_BLOCK_RADIUS_M':('BLOCK_RADIUS','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_BLOCK_VOLUME_M3':('BLOCK_VOLUME','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_TEMPERATURE_K':('STATIC_THERMAL_PROXY','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_PRESSURE_PA':('STATIC_PRESSURE_PROXY','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_PERMEABILITY_M2':('HIDDEN_POROUS_COVER_PARAMETER','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_LONGITUDE_RAD':('HIDDEN_BODY_FIXED_ANCHOR','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_SIN_LATITUDE':('HIDDEN_BODY_FIXED_ANCHOR','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_RETENTION_LOSS_KG':('STATIC_RETENTION_CHECK_RESULT','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_ATTEMPT_INDEX':('LOCAL_REJECTION_COUNTER','SOLAR_WATER_BLOCK_COMPILER_V1'),
           'GEN_HELIOCENTRIC_DISTANCE_AU':('SEALED_LATENT_OR_AUTHORIZED_DISTANCE','SOLAR_WATER_BLOCK_COMPILER_V1')}
    return [('wa_world.physical_property',dict(property_code=k,value_domain='NUMBER',
        physical_semantics_ref=v[0],schema_ref=v[1])) for k,v in known.items()]


def compile_body_world(body,row,policy,constraints,seed,scenario_id,scenario_key,model_id,
                       authorization_ref,science_cutoff,world_epoch,site_id,feature_id):
    """Pure body compiler; no database handle and no Agent-facing output."""
    key=body['semantic_key'];body_id=body['body_id'];domain='GEN_BODY_'+key+'_SITE_1'
    assertions=constraints['assertions'];materials=constraints['materials']
    # Local/sample material observations are provenance only for a generic body
    # block. A containment name is never an extrapolation warrant.
    physical_codes={'MASS':'mass','DYNAMICAL_MASS':'mass','MEAN_RADIUS':'radius',
        'GEOMETRIC_MEAN_DIAMETER':'radius','EFFECTIVE_DIAMETER':'radius',
        'BULK_DENSITY':'density'}
    used=[a for a in assertions if a['scope_kind']=='BODY' and
          a['property_code'] in physical_codes and
          _source_range(a,physical_codes[a['property_code']]) is not None]
    provenance=[dict(kind='ASSERTION',id=str(a['assertion_id']),support=str(a['support_id']),
        scope=a['scope_kind'],support_resolution=a['support_resolution'],
        representativeness=a['representativeness_lexeme'],ontology=a['ontology'],
        initial_standing=a['initial_standing'],standing=a['standing'],
        admission=str(a['admission_id']),decision_ordinal=a['decision_ordinal'],
        admission_authorization=a['authorization_ref'],use_contract=a['use_contract_ref'],
        source_id=str(a['source_id']),source_snapshot=str(a['snapshot_id']),
        source_artifact_id=str(a['source_artifact_id']) if a['source_artifact_id'] else None,
        knowledge_time_id=str(a['knowledge_time_id']) if a['knowledge_time_id'] else None,
        valid_time_id=str(a['valid_time_id']) if a['valid_time_id'] else None,
        lineage=a['lineage_lexeme'],metadata_sha256=a['metadata_sha256'],used=a in used)
        for a in assertions]
    provenance += [dict(kind='MATERIAL',id=str(m['evidence_id']),support=str(m['support_id']),
        scope=m['scope_kind'],support_resolution=m['support_resolution'],
        representativeness=m['representativeness_lexeme'],
        initial_standing=m['initial_standing'],standing=m['standing'],
        admission=str(m['admission_id']),decision_ordinal=m['decision_ordinal'],
        admission_authorization=m['authorization_ref'],use_contract=m['use_contract_ref'],
        source_id=str(m['source_id']),source_snapshot=str(m['snapshot_id']),
        source_snapshot_sha256=m['source_snapshot_sha256'],
        observation_id=str(m['observation_id']) if m['observation_id'] else None,
        sample_id=str(m['sample_id']) if m['sample_id'] else None,
        valid_time_id=str(m['valid_time_id']) if m['valid_time_id'] else None,
        material_family=m['material_family'],phase=m['phase_lexeme'],used=False)
        for m in materials]
    mass,radius,density=_dimensions(row,used,seed,key,domain)
    r_au=_interval(seed,key,domain,'heliocentric_distance',row['fallback_heliocentric_distance_min_au'],
        row['fallback_heliocentric_distance_max_au'],0)
    block=_block(row,policy,seed,key,domain,mass,radius,r_au)
    policy_input={'row':row,'shared_policy_sha256':POLICY_SHA,'table_sha256':TABLE_SHA,
        'source_snapshot_sha256':SOURCE_SHA,'admitted_constraint_dispositions':provenance,
        'cutoff':science_cutoff,'use_contract_ref':USE,'world_epoch':world_epoch}
    policy_bytes=canonical(policy_input);policy_hash=sha256(policy_bytes).hexdigest()
    policy_key='SOLAR_WATER_POLICY_'+key+'_'+str(model_id).split('-')[0]+'_'+policy_hash[:16]
    policy_id=_uuid('GENERATION_POLICY',policy_key,'1')
    world_id=_uuid('WORLD_REALIZATION',scenario_key+':'+key+':'+seed,'1')
    world_site_id=_uuid('WORLD_SITE',str(world_id)+':'+domain,'1')
    deposit_id=_uuid('WORLD_DEPOSIT',str(world_id)+':'+domain+':WATER_BEARING_MATERIAL','1')
    result_hash=_hash({'body':key,'world':str(world_id),'policy':policy_hash,'block':block,
                       'mass':mass,'radius':radius,'density':density})
    rows=[
        ('wa_world.generation_policy',dict(policy_id=policy_id,model_id=model_id,
            semantic_key=policy_key,version='1',body_id=body_id,
            property_code='WATER_BEARING_MATERIAL',policy_type_lexeme='AUTHORED_V0_3_CONDITIONAL_PRIOR',
            parameters=policy_input,parameter_schema_ref='SOLAR_HIDDEN_WORLD_SHARED_POLICY_v0.3',
            original_parameter_lexeme=None,policy_bytes=policy_bytes,policy_sha256=policy_hash,
            authorization_ref=authorization_ref,notes='Research prior; scoped admissions only; no reserve inference')),
        ('wa_world.realization',dict(world_id=world_id,scenario_id=scenario_id,model_id=model_id,
            policy_id=policy_id,body_id=body_id,semantic_key='SOLAR_WATER_WORLD_'+key+'_'+policy_hash[:16],
            world_seed_lexeme=seed,seed_lineage_ref='WORLD_STREAM:'+MODEL,
            scientific_cutoff_ordinal=science_cutoff,random_algorithm_ref='SHA256_FIRST64_DECIMAL_V1',
            key_schema_ref='LOOM_COMPARISON_RANDOM_V1',constraints_digest=_hash(provenance),
            generator_output_sha256=result_hash,status_lexeme='GENERATED_SCENARIO_NOT_SCIENTIFIC_EVIDENCE',
            created_time_lexeme=str(world_epoch),initial_epoch_id=None,world_context='SCENARIO')),
    ]
    for a in used:
        rows.append(('wa_world.constraint_binding',dict(world_id=world_id,body_id=body_id,
            binding_key='ASSERTION_'+str(a['assertion_id']),assertion_id=a['assertion_id'],
            admission_id=a['admission_id'],target_support_id=a['support_id'],extrapolation_warrant_id=None,
            assertion_metadata_sha256=a['metadata_sha256'],binding_role='BODY_PHYSICAL_PARAMETER_AT_SOURCE_SUPPORT',
            use_contract_ref=USE)))
    rows += [
        ('wa_world.site',dict(site_id=world_site_id,world_id=world_id,body_id=body_id,
            location_id=site_id,semantic_key=domain,name=body['canonical_name']+' generated prospecting domain',
            status_lexeme='HIDDEN_FICTIONAL_SITE',refinement_model_ref=MODEL,
            refinement_seed_lineage_ref='WORLD:'+seed,realization_sha256=result_hash)),
        ('wa_world.deposit',dict(deposit_id=deposit_id,world_id=world_id,body_id=body_id,
            site_id=world_site_id,location_id=feature_id,resource_class='WATER_BEARING_MATERIAL',
            geometry_class_lexeme='BOUNDED_SPHERE_MODEL',initial_in_situ_state='KNOWN',
            initial_in_situ_quantity=block['target_mass_kg'],unit_key=UNITS['mass'],
            concentration_state='KNOWN',concentration_value=block['target_fraction'],
            concentration_unit_key=UNITS['fraction'],vertical_id=None,
            phase_ref=block['form'],physical_form_ref=block['subtype'],
            original_accessibility_lexeme='UNKNOWN_UNTIL_CAPABILITY_ASSESSMENT',
            provenance_ref='PR147:'+RESEARCH_COMMIT+':'+result_hash)),
        _state(world_id,body_id,None,'GEN_BODY_MASS_KG',mass,UNITS['mass'],'FINITE_MODELED_BODY_MASS'),
        _state(world_id,body_id,None,'GEN_BODY_RADIUS_M',radius,UNITS['length'],'MODELED_BODY_RADIUS'),
        _state(world_id,body_id,None,'GEN_BODY_BULK_DENSITY',density,UNITS['density'],'MODELED_BODY_BULK_DENSITY'),
        _state(world_id,body_id,None,'GEN_HELIOCENTRIC_DISTANCE_AU',r_au,UNITS['distance'],'LATENT_OR_ADMITTED_ORBITAL_CONTEXT'),
        _state(world_id,body_id,feature_id,'GEN_BLOCK_HOST_MASS_KG',block['host_mass_kg'],UNITS['mass'],'FINITE_HOST_MASS'),
        _state(world_id,body_id,feature_id,'GEN_BLOCK_DENSITY',block['density_kg_m3'],UNITS['density'],'MODELED_BLOCK_DENSITY'),
        _state(world_id,body_id,feature_id,'GEN_TARGET_FRACTION',block['target_fraction'],UNITS['fraction'],'MATERIAL_FORM_SPECIFIC_TARGET'),
        _state(world_id,body_id,feature_id,'GEN_BLOCK_TOP_DEPTH_M',block['depth_m'],UNITS['length'],'UNCONSTRAINED_HIDDEN_PLACEMENT'),
        _state(world_id,body_id,feature_id,'GEN_BLOCK_RADIUS_M',block['radius_m'],UNITS['length'],'MASS_DENSITY_DERIVED_RADIUS'),
        _state(world_id,body_id,feature_id,'GEN_BLOCK_VOLUME_M3',block['volume_m3'],UNITS['volume'],'MASS_DIVIDED_BY_BLOCK_DENSITY'),
        _state(world_id,body_id,feature_id,'GEN_TEMPERATURE_K',block['temperature_k'],UNITS['temperature'],'STATIC_ENVIRONMENT_PROXY'),
        _state(world_id,body_id,feature_id,'GEN_PRESSURE_PA',block['pressure_pa'],UNITS['pressure'],'STATIC_ENVIRONMENT_PROXY'),
        _state(world_id,body_id,feature_id,'GEN_PERMEABILITY_M2',block['permeability_m2'],UNITS['area'],'STATIC_COVER_PARAMETER'),
        _state(world_id,body_id,feature_id,'GEN_LONGITUDE_RAD',block['longitude_rad'],UNITS['angle'],'BODY_FIXED_EQUAL_AREA_ANCHOR'),
        _state(world_id,body_id,feature_id,'GEN_SIN_LATITUDE',block['sin_latitude'],UNITS['fraction'],'BODY_FIXED_EQUAL_AREA_ANCHOR'),
        _state(world_id,body_id,feature_id,'GEN_RETENTION_LOSS_KG',block['retention_loss_kg'],UNITS['mass'],'STATIC_RETENTION_RESULT'),
        _state(world_id,body_id,feature_id,'GEN_ATTEMPT_INDEX',D(block['attempt']),UNITS['fraction'],'LOCAL_REJECTION_ATTEMPT'),
        _state(world_id,body_id,feature_id,'R_IN_SITU',block['target_mass_kg'],UNITS['mass'],'HOST_MASS_TIMES_TARGET_FRACTION'),
        _state(world_id,body_id,feature_id,'R_ACCESSIBLE',None,None,'UNKNOWN_UNTIL_CAPABILITY'),
        _state(world_id,body_id,feature_id,'R_RECOVERABLE',None,None,'UNKNOWN_UNTIL_COMPATIBLE_PROCESS'),
        _state(world_id,body_id,feature_id,'R_RESERVE',None,None,'UNKNOWN_ECONOMIC_INTERPRETATION'),
    ]
    return tuple(rows),dict(body_key=key,body_name=body['canonical_name'],body_id=body_id,
        scenario_id=scenario_id,scenario_key=scenario_key,model_id=model_id,policy_id=policy_id,world_id=world_id,
        world_site_id=world_site_id,deposit_id=deposit_id,site_id=site_id,feature_id=feature_id,
        resource_class='WATER_BEARING_MATERIAL',block=block,result_hash=result_hash)


def bind_generated_target(bound_world,activity_profile):
    """Adapt one trusted private block to the existing 6E resource operator."""
    from simulation.offworld_mvp.phase3b.kernel.offworld_kernel.mvp_state import ScenarioResource
    required={'resource_id','node_id','max_depth_m','max_temperature_k',
              'max_pressure_pa','compatible_forms','recovery_yield','kg_per_model_unit'}
    if set(activity_profile)!=required:raise GenerationBlocked('ACTIVITY_PROFILE_FIELDS')
    if 'block' in bound_world:
        block=bound_world['block']
        initial=remaining=block['target_mass_kg']
    else:
        # This is the fixed trusted projection returned by the existing
        # World Authority run_epoch.load_bound_world reader after restart.
        deposits=tuple(d for d in bound_world['deposits']
            if d['resource_class']=='WATER_BEARING_MATERIAL')
        if len(deposits)!=1:raise GenerationBlocked('GENERATED_TARGET_CARDINALITY')
        deposit=deposits[0]
        if deposit['initial_in_situ_state']!='KNOWN' or deposit['unit_key']!=UNITS['mass']:
            raise GenerationBlocked('GENERATED_TARGET_UNIT_OR_STATE')
        values={s['property_code']:s for s in bound_world['hidden_states']
            if s['location_id']==deposit['location_id']}
        required_states={'GEN_BLOCK_TOP_DEPTH_M':UNITS['length'],
                         'GEN_TEMPERATURE_K':UNITS['temperature'],
                         'GEN_PRESSURE_PA':UNITS['pressure']}
        for prop,unit in required_states.items():
            state=values.get(prop)
            if state is None or state['value_state']!='KNOWN' or state['unit_key']!=unit:
                raise GenerationBlocked('GENERATED_TARGET_ENVIRONMENT:'+prop)
        initial=D(deposit['initial_in_situ_quantity'])
        block={'form':deposit['phase_ref'],'target_mass_kg':initial,
               'depth_m':D(values['GEN_BLOCK_TOP_DEPTH_M']['numeric_value']),
               'temperature_k':D(values['GEN_TEMPERATURE_K']['numeric_value']),
               'pressure_pa':D(values['GEN_PRESSURE_PA']['numeric_value'])}
        history=tuple(s for s in bound_world['stock_history'] if s['deposit_id']==deposit['deposit_id'])
        if history:
            final=history[-1]
            if final['remaining_state']!='KNOWN' or final['unit_key']!=UNITS['mass']:
                raise GenerationBlocked('GENERATED_STOCK_STATE')
            remaining=D(final['remaining_in_situ'])
        else:remaining=initial
        if not D(0)<=remaining<=initial:raise GenerationBlocked('GENERATED_STOCK_CONSERVATION')
    reach=D(str(activity_profile['max_depth_m']))
    yield_fraction=D(str(activity_profile['recovery_yield']))
    max_temp=D(str(activity_profile['max_temperature_k']))
    max_pressure=D(str(activity_profile['max_pressure_pa']))
    kg_per_unit=D(str(activity_profile['kg_per_model_unit']))
    if (not all(v.is_finite() for v in (reach,yield_fraction,max_temp,max_pressure,kg_per_unit))
        or reach<0 or max_temp<0 or max_pressure<0 or kg_per_unit<=0 or not 0<=yield_fraction<=1):
        raise GenerationBlocked('ACTIVITY_PROFILE_RANGE')
    compatible=activity_profile['compatible_forms']
    if not isinstance(compatible,(tuple,list)) or not compatible or any(
        f not in ('DRY_MATRIX','MINERAL_BOUND_H2O_OH','FREE_ICE') for f in compatible):
        raise GenerationBlocked('ACTIVITY_PROFILE_FORMS')
    within_limits=(block['depth_m']<=reach and block['temperature_k']<=max_temp
                   and block['pressure_pa']<=max_pressure)
    if block['form'] not in compatible:
        accessible=initial if within_limits else D(0)
        recoverable=remaining_recoverable=D(0)
    else:
        accessible=initial if within_limits else D(0)
        recoverable=accessible*yield_fraction
        remaining_recoverable=remaining*yield_fraction if accessible>0 else D(0)
    return ScenarioResource(activity_profile['resource_id'],activity_profile['node_id'],
        'WATER_BEARING_MATERIAL',initial/kg_per_unit,accessible/kg_per_unit,
        recoverable/kg_per_unit,remaining_recoverable/kg_per_unit)


def generate_solar_system(reference_reader,science_writer,world_writer,*,seed,authorization_ref,
                          science_cutoff,world_epoch=2026,return_bindings=False):
    """Compile all current eligible WA bodies, then seal one exact WORLD batch."""
    if not seed or not authorization_ref or type(science_cutoff) is not int or science_cutoff<0 or world_epoch!=2026:
        raise GenerationBlocked('GENERATION_DECLARATION')
    table,policy=load_inputs()
    catalog=store.read_generation_catalog(reference_reader,SOURCE_SHA)
    unknown=[b['semantic_key'] for b in catalog if b['semantic_key'] not in table]
    if unknown:raise GenerationBlocked('MISSING_PRIOR_ROWS:'+','.join(unknown))
    eligible=[]
    for body in catalog:
        row=table[body['semantic_key']]
        if row['material_model_applicability'] in ('SOLID','SOLID_WITH_ATMOSPHERE'):
            if row['body_class']!=body['body_class']:
                raise GenerationBlocked('BODY_CLASS_MISMATCH:'+body['semantic_key'])
            eligible.append((body,row))
    if not eligible:raise GenerationBlocked('NO_ELIGIBLE_BODIES')
    code_sha=sha256(Path(__file__).read_bytes()).hexdigest()
    model_version=code_sha[:16]
    scenario_key='SOLAR_WATER_'+_hash({'seed':seed,'epoch':world_epoch,'cutoff':science_cutoff,
        'source':SOURCE_SHA,'table':TABLE_SHA,'policy':POLICY_SHA,'code':code_sha})[:24]
    scenario_id=_uuid('SCENARIO',scenario_key,'1')
    model_id=_uuid('GENERATION_MODEL',MODEL,model_version)
    rows=[('wa_world.scenario',dict(scenario_id=scenario_id,semantic_key=scenario_key,version='1',
        definition_sha256=_hash({'source':SOURCE_SHA,'table':TABLE_SHA,'policy':POLICY_SHA,
            'seed':seed,'epoch':world_epoch,'cutoff':science_cutoff,'use':USE,'code':code_sha}),
        authorization_ref=authorization_ref,definition_locator='simulation/offworld_mvp/build6e/generated_world.py',
        world_context='SCENARIO')),
        ('wa_world.generation_model',dict(model_id=model_id,semantic_key=MODEL,version=model_version,
            name='Finite water-bearing prospecting block compiler',status_lexeme='AUTHORED_SCENARIO_MODEL',
            implementation_sha256=code_sha,implementation_locator='simulation/offworld_mvp/build6e/generated_world.py',
            model_family_ref=MODEL,uncertainty_contract_ref='PR147_V0_3_HIGH_SENSITIVITY',
            parameter_schema_ref='SOLAR_HIDDEN_WORLD_SHARED_POLICY_v0.3')),
        *_property_rows()]
    prepared=[]
    for body,row in eligible:
        key=body['semantic_key']
        constraints=store.read_generation_constraints(reference_reader,body['body_id'],science_cutoff,USE)
        site_key='GEN_BODY_'+key+'_SITE_1';feature_key='GEN_BODY_'+key+'_FEATURE_1'
        manifest=dict(profile='WA_GENERATED_SITE_METADATA_V1',authorization_ref=authorization_ref,
            body_key=key,site_key=site_key,feature_key=feature_key,
            site_name=body['canonical_name']+' generated prospecting site',
            feature_name=body['canonical_name']+' generated local feature',parent_location_key=None)
        site_id=store.stable_uuid('AUTHORED_LOCATION','LOOM_OFFWORLD_GENERATED_SITE_V1',
            store.length_prefixed(key,site_key).decode(),'IDENTITY_V1')
        feature_id=store.stable_uuid('AUTHORED_LOCATION','LOOM_OFFWORLD_GENERATED_SITE_V1',
            store.length_prefixed(key,feature_key).decode(),'IDENTITY_V1')
        compiled,binding=compile_body_world(body,row,policy,constraints,seed,scenario_id,scenario_key,
            model_id,authorization_ref,science_cutoff,world_epoch,site_id,feature_id)
        rows.extend(compiled);prepared.append((manifest,binding))
    for manifest,_ in prepared:
        store.install_generated_site_metadata(science_writer,manifest)
    status=store.install_exact_world(world_writer,rows)
    result=dict(status=status,body_count=len(prepared),scenario_id=str(scenario_id),
        sealed_world_digest=_hash([b['result_hash'] for _,b in prepared]),
        source_snapshot_sha256=SOURCE_SHA,prior_table_sha256=TABLE_SHA,shared_policy_sha256=POLICY_SHA)
    if return_bindings:
        result['_bindings']={binding['body_key']:binding for _,binding in prepared}
    return result


def main(argv=None):
    ap=argparse.ArgumentParser(description='Generate and seal the scoped hidden Solar System in World Authority')
    ap.add_argument('--reference-service',required=True)
    ap.add_argument('--science-writer-service',required=True)
    ap.add_argument('--world-writer-service',required=True)
    ap.add_argument('--world-seed',required=True)
    ap.add_argument('--authorization-ref',required=True)
    ap.add_argument('--science-cutoff',type=int,required=True)
    ap.add_argument('--world-epoch',type=int,default=2026)
    args=ap.parse_args(argv)
    import psycopg
    with psycopg.connect(service=args.reference_service) as reader, \
         psycopg.connect(service=args.science_writer_service) as science, \
         psycopg.connect(service=args.world_writer_service) as writer:
        result=generate_solar_system(reader,science,writer,seed=args.world_seed,
            authorization_ref=args.authorization_ref,science_cutoff=args.science_cutoff,
            world_epoch=args.world_epoch)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
