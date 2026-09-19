#!/usr/bin/env bash
# Reviewed, idempotent Lightsail preparation for Kevin. No mutation occurs without --approve.
set -euo pipefail

REGION="${AWS_REGION:-ap-southeast-2}"
ZONE="${LIGHTSAIL_ZONE:-ap-southeast-2a}"
INSTANCE="${LIGHTSAIL_INSTANCE_NAME:-loom-ceres-sydney-01}"
BLUEPRINT="${LIGHTSAIL_BLUEPRINT:-ubuntu_24_04}"
KEY_NAME="${LIGHTSAIL_KEY_NAME:-loom-ceres-sydney-01-key}"
KEY_FILE="${LIGHTSAIL_KEY_FILE:-$HOME/.ssh/$KEY_NAME.pem}"
SSH_CIDR=""
APPROVE=0
TEARDOWN=0
PUBLIC_HTTPS=0

usage() { echo "Usage: $0 [--ssh-cidr CIDR] [--allow-public-https] [--approve] [--teardown --approve]"; }
while (($#)); do
  case "$1" in
    --ssh-cidr) SSH_CIDR="${2:?CIDR required}"; shift 2;;
    --approve) APPROVE=1; shift;;
    --teardown) TEARDOWN=1; shift;;
    --allow-public-https) PUBLIC_HTTPS=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2;;
  esac
done
command -v aws >/dev/null || { echo "AWS CLI is required." >&2; exit 2; }
[[ "$REGION" == ap-southeast-2 ]] || { echo "Refusing non-Sydney region: $REGION" >&2; exit 2; }
[[ "$ZONE" =~ ^ap-southeast-2[abc]$ ]] || { echo "Invalid Sydney zone: $ZONE" >&2; exit 2; }

INSTANCE_ERR="$(mktemp)"
if INSTANCE_JSON="$(aws lightsail get-instance --region "$REGION" --instance-name "$INSTANCE" 2>"$INSTANCE_ERR")"; then
  echo "Instance already exists; no create action: $INSTANCE"
  if ((TEARDOWN)); then
    ((APPROVE)) || { echo "Teardown requires --approve." >&2; exit 2; }
    aws lightsail delete-instance --region "$REGION" --instance-name "$INSTANCE"
    echo "Deleted $INSTANCE. Key pair was retained: $KEY_NAME"
  fi
  exit 0
fi
if ! grep -Eqi 'not.?found|does not exist|unknown instance' "$INSTANCE_ERR"; then
  cat "$INSTANCE_ERR" >&2; rm -f "$INSTANCE_ERR"; echo "Cannot establish instance absence; refusing to continue." >&2; exit 1
fi
rm -f "$INSTANCE_ERR"
((TEARDOWN)) && { echo "No instance exists; nothing to tear down."; exit 0; }

BUNDLE_JSON="$(aws lightsail get-bundles --region "$REGION" --no-include-inactive --output json)"
BUNDLE_ID="$(printf '%s' "$BUNDLE_JSON" | python3 -c 'import json,sys
x=json.load(sys.stdin)["bundles"]
r=[b for b in x if b.get("ramSizeInGb")==4 and b.get("cpuCount")==2 and b.get("diskSizeInGb")==80 and b.get("price")==24.0 and b.get("isActive") is True and b.get("publicIpv4AddressCount",1)==1]
if len(r)!=1: raise SystemExit("expected one active public-IPv4 bundle, found %d: %s" % (len(r), [b.get("bundleId") for b in r]))
print(r[0]["bundleId"])')"
echo "Validated bundle: $BUNDLE_ID (4 GB RAM, 2 vCPU, 80 GB, US\$24/month, public IPv4)"
[[ -n "$SSH_CIDR" ]] || { echo "--ssh-cidr is required before approval." >&2; exit 2; }
[[ "$SSH_CIDR" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}/32$ ]] || { echo "Use a single IPv4 /32 SSH CIDR." >&2; exit 2; }
aws lightsail get-blueprints --region "$REGION" --query "blueprints[?blueprintId=='$BLUEPRINT' && isActive==\`true\`].blueprintId" --output text | grep -qx "$BLUEPRINT"
aws lightsail get-regions --region "$REGION" --query "regions[?name=='$REGION'].name" --output text | grep -qx "$REGION"
echo "Validated region $REGION, zone $ZONE, blueprint $BLUEPRINT; no existing instance."
((APPROVE)) || { echo "DRY RUN: re-run with --approve to create the key pair, instance and firewall rules."; exit 0; }

mkdir -p "$(dirname "$KEY_FILE")"
umask 077
if ! aws lightsail get-key-pair --region "$REGION" --key-pair-name "$KEY_NAME" >/dev/null 2>&1; then
  [[ ! -e "$KEY_FILE" ]] || { echo "Refusing to overwrite existing key file: $KEY_FILE" >&2; exit 1; }
  tmp_key="$(mktemp "${KEY_FILE}.XXXXXX")"
  trap 'rm -f "$tmp_key"' EXIT
  aws lightsail create-key-pair --region "$REGION" --key-pair-name "$KEY_NAME" --query privateKeyBase64 --output text | base64 -d > "$tmp_key"
  [[ -s "$tmp_key" ]] || { echo "AWS returned an empty private key." >&2; exit 1; }
  chmod 600 "$tmp_key"; mv -n "$tmp_key" "$KEY_FILE"
else
  [[ -f "$KEY_FILE" ]] || { echo "Key pair exists remotely but custody file is absent: $KEY_FILE" >&2; exit 1; }
  chmod 600 "$KEY_FILE"
fi
aws lightsail create-instances --region "$REGION" --instance-names "$INSTANCE" --availability-zone "$ZONE" --blueprint-id "$BLUEPRINT" --bundle-id "$BUNDLE_ID" --key-pair-name "$KEY_NAME" --tags key=loom-purpose,value=ceres-atlas,key=loom-managed,value=true
PORTS_JSON="[{\"fromPort\":22,\"toPort\":22,\"protocol\":\"tcp\",\"cidrs\":[\"$SSH_CIDR\"]}]"
if ((PUBLIC_HTTPS)); then PORTS_JSON="${PORTS_JSON%]} ,{\"fromPort\":443,\"toPort\":443,\"protocol\":\"tcp\",\"cidrs\":[\"0.0.0.0/0\"]}]"; fi
aws lightsail put-instance-public-ports --region "$REGION" --instance-name "$INSTANCE" --port-infos "$PORTS_JSON"
aws lightsail get-instance --region "$REGION" --instance-name "$INSTANCE" --query 'instance.{name:name,state:state,ip:publicIp,zone:location.availabilityZone,bundle:bundleId,blueprint:blueprintId}' --output table
echo "Provisioned infrastructure only. No LOOM deployment was performed."
