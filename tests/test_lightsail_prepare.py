import json, os, stat, subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / 'tools/aws/prepare_lightsail_ceres.sh'
BUNDLES = {'bundles': [{'bundleId':'medium_3_0','ramSizeInGb':4,'cpuCount':2,'diskSizeInGb':80,'price':24.0,'isActive':True,'publicIpv4AddressCount':1}]}

def fake(tmp, mode='absent'):
    bindir = tmp/'bin'; bindir.mkdir(); log=tmp/'calls';
    aws = bindir/'aws'
    aws.write_text(f'''#!/bin/sh
printf '%s\\n' "$*" >> "{log}"
case "$*" in
*"get-instance"*)
  if [ "{mode}" = existing ]; then echo '{{"name":"loom-ceres-sydney-01"}}'; exit 0; fi
  echo 'NotFoundException: instance does not exist' >&2; exit 254;;
*"get-bundles"*) printf '%s' '{json.dumps(BUNDLES)}';;
*"get-blueprints"*) echo ubuntu_24_04;;
*"get-regions"*) echo ap-southeast-2;;
*) :;;
esac
'''); aws.chmod(0o755)
    return bindir, log

def run(tmp, mode='absent', *args):
    bindir, log = fake(tmp, mode)
    env={**os.environ, 'PATH':f'{bindir}:{os.environ["PATH"]}', 'HOME':str(tmp), 'LIGHTSAIL_KEY_FILE':str(tmp/'key.pem')}
    return subprocess.run([str(SCRIPT), '--ssh-cidr','203.0.113.7/32', *args], env=env, text=True, capture_output=True)

def test_dry_run_resolves_bundle_without_mutation(tmp_path):
    r=run(tmp_path)
    assert r.returncode == 0, r.stderr
    assert 'medium_3_0' in r.stdout
    calls=(tmp_path/'calls').read_text()
    assert 'create-instances' not in calls and 'put-instance-public-ports' not in calls

def test_existing_instance_is_idempotent(tmp_path):
    r=run(tmp_path, 'existing', '--approve')
    assert r.returncode == 0
    assert 'already exists' in r.stdout
    assert 'create-instances' not in (tmp_path/'calls').read_text()

def test_duplicate_bundle_fails_closed(tmp_path):
    bindir, log=fake(tmp_path)
    aws=bindir/'aws'; text=aws.read_text().replace(json.dumps(BUNDLES), json.dumps({'bundles': BUNDLES['bundles'] * 2}))
    aws.write_text(text)
    env={**os.environ,'PATH':f'{bindir}:{os.environ["PATH"]}','HOME':str(tmp_path)}
    r=subprocess.run([str(SCRIPT),'--ssh-cidr','203.0.113.7/32'],env=env,text=True,capture_output=True)
    assert r.returncode != 0 and 'expected one active' in r.stderr

def test_public_ssh_cidr_is_rejected(tmp_path):
    r=run(tmp_path, 'absent', '--ssh-cidr', '0.0.0.0/0')
    assert r.returncode != 0 and '/32' in r.stderr
