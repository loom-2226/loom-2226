# Phase 3B Financing Request / Decision Protocol 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / BUILD-5 ENTRY INTERFACE
**Autonomous policy authority:** NOT GRANTED

## Request

A Build 5 financing request is immutable and must declare:

- request id/year;
- sponsor and project;
- positive requested amount;
- project stage;
- disclosed observation ids;
- exact required underwriting keys;
- exact required belief keys;
- exact required prior keys;
- currency/unit;
- protocol version.

The exact required underwriting keys are:

- `underwriting.PRICE`;
- `underwriting.EXPLORATION_CAPEX`;
- `underwriting.DEVELOPMENT_CAPEX`;
- `underwriting.OPERATING_COST`;
- `underwriting.LEAD_TIME`.

The Build 5 Test 001 request also declares required decision-state dependencies:

- belief key `resource_exists`;
- prior key `resource_exists`.

An absent required belief or prior is UNKNOWN for decision purposes.

## Decision outcomes

Allowed outcomes are exactly:

- `APPROVE`;
- `REJECT`;
- `DEFER`;
- `BLOCKED_UNKNOWN`.

A decision also carries financier id, amount, instrument, human-readable reason, machine reason code, unknown-input keys, pinned input-snapshot reference, policy version, and decision version.

The reason-code register includes, among others, `BELOW_RETURN`, `CEILING`, `CONCENTRATION`, and `BLOCKED_REQUIRED_INPUT_UNKNOWN`.

## Semantics

`APPROVE` requires:

- `approved=true`;
- positive amount;
- instrument;
- amount not exceeding the request.

All non-APPROVE outcomes require:

- `approved=false`;
- amount exactly zero.

If any required underwriting input, required belief, or required prior is unknown, the decision must be `BLOCKED_UNKNOWN`; a generic REJECT or DEFER may not hide required UNKNOWN inputs.

`BLOCKED_UNKNOWN` requires reason code `BLOCKED_REQUIRED_INPUT_UNKNOWN` and at least one explicit unknown-input key.

The schema does not execute financing. It only defines the decision artifact. Any later commitment/disbursement remains a separate scheduler/kernel transition.
