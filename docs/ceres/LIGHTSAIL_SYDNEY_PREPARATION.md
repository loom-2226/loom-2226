# Ceres Atlas Lightsail Sydney preparation

This is a reviewed preparation artifact only. It does not provision AWS, deploy LOOM, publish databases, or modify canonical data.

The target is `ap-southeast-2`, zone `ap-southeast-2a` by default, Ubuntu `ubuntu_24_04`, instance `loom-ceres-sydney-01`, and the active public-IPv4 bundle resolved at runtime from `get-bundles`. The expected match is `medium_3_0`: 4 GB RAM, 2 vCPU, 80 GB SSD, US$24/month. AWS documents the same specification and price in its Lightsail bundle table ([AWS bundle reference](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bundles.html)). The script refuses to proceed unless the live API returns exactly one active matching bundle, so a changed bundle catalog fails closed.

Run from a machine with AWS CLI credentials scoped to Lightsail read access for dry-run validation:

```sh
./tools/aws/prepare_lightsail_ceres.sh --ssh-cidr YOUR.PUBLIC.IP/32
```

The script checks the region, zone, Ubuntu blueprint, exact bundle, and existing instance. It performs no mutation without the explicit gate:

```sh
./tools/aws/prepare_lightsail_ceres.sh --ssh-cidr YOUR.PUBLIC.IP/32 --approve
```

Approval creates or reuses a named Lightsail key pair, writes a new private key only when no local key exists, applies mode `600`, creates the instance with immutable purpose tags, and opens only TCP/22 from the supplied `/32` plus TCP/443. It does not install software or deploy the Atlas. The script is idempotent: an existing named instance causes it to report and exit without creating another.

Expected recurring cost is US$24/month for the public-IPv4 plan, with the regional transfer allowance shown by the live bundle response. Additional charges may apply for outbound transfer beyond the allowance, static IPs, snapshots, block storage, managed databases, DNS, taxes, or other AWS services. No such extras are requested here.

Post-provisioning verification is the final `get-instance` table emitted by the script: instance name, running state, public IP, availability zone, bundle and blueprint. Any later deployment must separately verify SSH from the approved `/32`, HTTPS certificate and access control, then the private GHCR image and external read-only database mounts. This preparation does not perform those actions.

Teardown, requiring the same explicit gate, deletes only the named instance and retains the key pair for review:

```sh
./tools/aws/prepare_lightsail_ceres.sh --teardown --approve
```

Delete the named key pair and local PEM only after confirming no other instance uses them, using the AWS console or an independently reviewed command. Snapshots and static IPs, if created later, must be enumerated and deleted separately; they are not silently removed by this script.

At last checked from the governing request, no existing Sydney instance matched this name. The local environment used for preparation does not have AWS CLI installed, so a live API result and account-level cost estimate remain pending Kevin's approved execution environment.
