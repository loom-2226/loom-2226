"""Versioned exact continuation envelope; no economic calculations."""
from pathlib import Path
import hashlib
import json
import os
import pickle
import platform
import struct
import sys
import zipfile

FORMAT = 'LOOM_EARTH_COMPLETE_CONTINUATION'
VERSION = 1
MODEL = 'v0.6.1-d1-c1'
STATE_FIELDS = (
    'isos','base','state','asset_state','asset_dep','labor_shares','investment_shares',
    'current_tfp','current_gap','synthetic_ratio','previous_tech_multiplier',
    'base_compute_enabling_per_worker','base_automation_per_worker','base_energy_go_per_worker',
    'base_go60','base_va60','base_inv60','prev_country_va','prev_country_inv','prev_global_va',
    'baseline_trade','current_trade','topology_meta','demo_pop','demo_wap',
    'pop_tail_anchor','wap_tail_anchor','tfp_calibration',
    'country_rows','sector_rows','asset_rows','max_capital_identity','max_employment_recon',
    'max_labor_share_move','max_investment_share_move','max_trade_tv_move','max_trade_component_move',
    'max_synthetic_ratio_move','max_tech_multiplier_log_move','max_synthetic_ratio_level',
    'min_replacement_coverage','min_country_growth','max_country_growth',
    'annual_gate_failures','checkpoints',
)


class CheckpointError(ValueError):
    pass


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def json_bytes(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def fingerprint(value):
    """Type-tagged, order-sensitive digest, preserving all binary64 bits.

    Aliasing is intentionally not part of numerical-state equality; pickle still
    preserves references within the stored bundle. Integers/strings are length
    framed; containers carry their length. Dict entries follow insertion order.
    """
    h=hashlib.sha256()
    def framed(tag,data):
        h.update(tag);h.update(struct.pack('>Q',len(data)));h.update(data)
    def visit(v):
        t=type(v)
        if v is None:h.update(b'N')
        elif t is bool:h.update(b'T' if v else b'F')
        elif t is int:framed(b'I',str(v).encode('ascii'))
        elif t is float:h.update(b'D');h.update(struct.pack('>d',v))
        elif t is str:framed(b'S',v.encode('utf-8'))
        elif t in (tuple,list):
            h.update(b'Q' if t is tuple else b'L');h.update(struct.pack('>Q',len(v)))
            for x in v:visit(x)
        elif t is dict:
            h.update(b'M');h.update(struct.pack('>Q',len(v)))
            for k,x in v.items():visit(k);visit(x)
        else:raise CheckpointError('Unsupported state type: '+str(t))
    visit(value)
    return h.hexdigest()


def runtime_identity():
    return {'python':sys.version,'implementation':sys.implementation.name,
            'cache_tag':sys.implementation.cache_tag,'machine':platform.machine(),
            'libc':list(platform.libc_ver()),'byteorder':sys.byteorder,
            'mantissa_bits':sys.float_info.mant_dig}


def constants_snapshot(namespace):
    def normalize(v):
        if type(v) is set:return ('MEMBERSHIP_SET',tuple(sorted(v)))
        if type(v) is dict:return {k:normalize(x) for k,x in v.items()}
        if type(v) is tuple:return tuple(normalize(x) for x in v)
        if type(v) is list:return [normalize(x) for x in v]
        return v
    return {k:normalize(v) for k,v in sorted(namespace.items())
            if k.isupper() and not k.startswith('_')
            and type(v) in (bool,int,float,str,tuple,list,dict,set)}


def compatibility(namespace,runner):
    constants=constants_snapshot(namespace)
    return {'model_version':MODEL,'runner_sha256':sha(runner),
            'checkpoint_io_sha256':sha(__file__),'runtime':runtime_identity(),
            'constants_fingerprint':fingerprint(constants)},constants


class HashingWriter:
    def __init__(self,stream):self.stream=stream;self.hash=hashlib.sha256()
    def write(self,data):self.hash.update(data);return self.stream.write(data)


class BuiltinsOnlyUnpickler(pickle.Unpickler):
    def find_class(self,module,name):
        raise CheckpointError('Executable/object pickle reference rejected')


def save(path,year,local_state,compat,constants,input_hashes):
    path=Path(path)
    if path.exists():raise CheckpointError('Refusing to overwrite checkpoint')
    state={k:(tuple(local_state[k]) if k=='isos' else local_state[k]) for k in STATE_FIELDS}
    component_hashes={k:fingerprint(v) for k,v in state.items()}
    manifest={'format':FORMAT,'format_version':VERSION,**compat,'current_year':year,
              'next_year':year+1,'boundary':'AFTER_ANNUAL_COMMIT_GATES_AND_SUMMARY',
              'input_hashes':input_hashes,'calibration_fingerprint':fingerprint(state['tfp_calibration']),
              'calibration_observation_fingerprint':state['tfp_calibration']['ordering_audit']['observation_sequence_sha256'],
              'component_fingerprints':component_hashes,
              'complete_state_fingerprint':fingerprint(component_hashes),
              'state_fields':list(STATE_FIELDS),'row_counts':{k:len(state[k]) for k in ('country_rows','sector_rows','asset_rows')},
              'trade_nodes':len(state['current_trade']),
              'trade_components':sum(len(x) for x in state['current_trade'].values())}
    temp=path.with_suffix(path.suffix+'.partial')
    if temp.exists():raise CheckpointError('Partial checkpoint already exists')
    with zipfile.ZipFile(temp,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        with z.open('state.pickle','w',force_zip64=True) as stream:
            writer=HashingWriter(stream)
            pickle.dump({'state':state,'constants':constants},writer,protocol=5)
            manifest['payload_sha256']=writer.hash.hexdigest()
        manifest['integrity_sha256']=hashlib.sha256(json_bytes(manifest)).hexdigest()
        z.writestr('manifest.json',json_bytes(manifest))
    os.replace(temp,path)
    print(f'[COMPLETE CHECKPOINT] {year}: {path} state={manifest["complete_state_fingerprint"]}',flush=True)
    return manifest


def load(path,compat,constants):
    try:
        with zipfile.ZipFile(path) as z:
            if sorted(z.namelist())!=['manifest.json','state.pickle']:
                raise CheckpointError('Unexpected checkpoint members')
            manifest=json.loads(z.read('manifest.json'))
            digest=manifest.pop('integrity_sha256')
            if hashlib.sha256(json_bytes(manifest)).hexdigest()!=digest:
                raise CheckpointError('Checkpoint integrity hash mismatch')
            manifest['integrity_sha256']=digest
            if manifest['format']!=FORMAT or manifest['format_version']!=VERSION:
                raise CheckpointError('Incompatible checkpoint format/version')
            for key,value in compat.items():
                if manifest.get(key)!=value:raise CheckpointError('Incompatible '+key)
            if manifest['state_fields']!=list(STATE_FIELDS):raise CheckpointError('Incompatible state inventory')
            with z.open('state.pickle') as stream:
                if hashlib.file_digest(stream,'sha256').hexdigest()!=manifest['payload_sha256']:
                    raise CheckpointError('Checkpoint payload integrity mismatch')
            with z.open('state.pickle') as stream:
                bundle=BuiltinsOnlyUnpickler(stream).load()
            if type(bundle) is not dict or set(bundle)!= {'state','constants'}:
                raise CheckpointError('Invalid checkpoint bundle')
            state=bundle['state']
            if type(state) is not dict or list(state)!=list(STATE_FIELDS):
                raise CheckpointError('Invalid ordered state inventory')
            if fingerprint(bundle['constants'])!=fingerprint(constants):
                raise CheckpointError('Checkpoint constants mismatch')
            fields={k:fingerprint(v) for k,v in state.items()}
            if fields!=manifest['component_fingerprints'] or fingerprint(fields)!=manifest['complete_state_fingerprint']:
                raise CheckpointError('Decoded state integrity mismatch')
            if fingerprint(state['tfp_calibration'])!=manifest['calibration_fingerprint']:
                raise CheckpointError('Calibration mismatch')
            year=manifest['current_year']
            if type(year) is not int or not constants['START_YEAR']<=year<=constants['END_YEAR'] or manifest['next_year']!=year+1:
                raise CheckpointError('Invalid checkpoint year')
            if state['annual_gate_failures']:raise CheckpointError('Cannot resume a failed boundary')
            return state,manifest
    except CheckpointError:raise
    except (KeyError,TypeError,ValueError,zipfile.BadZipFile,EOFError,pickle.UnpicklingError) as e:
        raise CheckpointError('Malformed checkpoint: '+str(e)) from e
