"""PR 3B: 90 catalog bodies in one conserved Route 1 campaign (TEST_ONLY).

This opt-in scenario buys abstract study services, not physical missions.
The four Build 6C results are authored scenario standings, never generated truth.
"""
from collections import Counter, defaultdict
from decimal import Decimal as D
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

from offworld_kernel.mvp_state import Observation
from offworld_kernel.named_portfolio import load_build6c_scenario
from simulation.offworld_mvp.build6e.generated_world import load_inputs
from simulation.offworld_mvp.build7.opportunities import REFERENCE
from .route1_body_campaign import (
    BodyCampaign, HISTORICAL_BODIES, ORDER, SETTINGS, SPONSORS, decade_counts,
)

AUTHORING = {
    'BENNU': ('BENNU-A1-RESOURCE', 'BENNU-A2-CONCEPT'),
    'CERES': ('CERES-A1-SURFACE', 'CERES-A2-ASSESS'),
    'MARS': ('MARS-A1-REMOTE', 'MARS-A2-SURFACE'),
    'MOON': ('MOON-A1-SURFACE', 'MOON-A2-ASSESS'),
}
PR3B_SETTINGS = {
    'A1_REOPEN_ON': ('INSUFFICIENT', 'NO_RESULT'),
    'A1_REOPEN_AT': 'NEXT_YEARLY_DECISION_AFTER_REVIEW',
    'A1_RETRY_LIMIT': None,
    'A1_RETRY_DRAW_KEY': 'A1_REVIEW_SEED|BODY|A1|ATTEMPT (first attempt unchanged)',
    'MAX_ACTIVE_CLAIMANTS_PER_BODY': 1,
    'SPONSOR_ALLOCATION_ORDER': 'REPEATED_CAST_ID_ROUNDS',
    'A1_RESULT_SOURCE': 'BUILD6C_AUTHORED_OR_SHA256_TEST_ONLY',
    'CHECKPOINT_BODY_COUNT': 45,
    'BODY_COUNT': 90,
    'ACCESS_UNKNOWN_TREATMENT': 'ABSTRACT_STUDY_ONLY_NO_TRAJECTORY',
    'MAX_NEW_STAGES_PER_SPONSOR_YEAR': None,
}
ALL_BODIES = tuple(sorted(k for k, row in load_inputs()[0].items()
                          if row['material_model_applicability']
                          in ('SOLID', 'SOLID_WITH_ATMOSPHERE')))
assert len(ALL_BODIES) == 90 and set(AUTHORING) == HISTORICAL_BODIES
REFERENCE_STATUS = {
    row['body_id']: row['accessibility_status']
    for row in json.loads(Path(REFERENCE).read_text())['records']
}
assert set(REFERENCE_STATUS) == set(ALL_BODIES)
assert Counter(REFERENCE_STATUS.values()) == {'DERIVABLE': 83, 'UNKNOWN': 7}


def review_draw(body, attempt):
    """Existing PR 3A first draw preserved; retries are separate paid draws."""
    key = f"{SETTINGS['A1_REVIEW_SEED']}|{body}|A1"
    if attempt != 1:
        key += f'|{attempt}'
    return D(int.from_bytes(sha256(key.encode()).digest(), 'big')) / D(2**256)


class AllBodyCampaign(BodyCampaign):
    def __init__(self, body_count=90, ceilings_enabled=True,
                 participating_sponsors=None, failures=()):
        if body_count not in (45, 90):
            raise ValueError('only the explicit 45-body checkpoint or 90-body run')
        super().__init__(ceilings_enabled=ceilings_enabled,
                         participating_sponsors=participating_sponsors)
        self.body_count = body_count
        self.bodies = (ALL_BODIES if body_count == 90 else tuple(sorted(
            set(AUTHORING) | set([b for b in ALL_BODIES if b not in AUTHORING][:41]))))
        assert len(self.bodies) == body_count
        self.max_stages = None
        self.portfolio = load_build6c_scenario()
        for body, ids in AUTHORING.items():
            for stage, aid in zip(('A1', 'A2'), ids):
                if self.portfolio.activity(aid).body_id != body:
                    raise AssertionError('authored activity/body mismatch')
        self.injected_failures = frozenset(failures)
        if any((body not in self.bodies or stage not in ('A1','A2')
                or type(attempt) is not int or attempt < 1)
               for body, stage, attempt in self.injected_failures):
            raise ValueError('bad TEST_ONLY stage failure identity')
        self.a1_counts = Counter()
        self.last_a1_year = {}
        self.completed = set()
        self.pending = []
        self.reviewed_receipts = set()
        self.body_yearly = []
        self.year_seconds = {}
        self._year_start = {}
        self.supplier_spend = defaultdict(lambda: D(0))
        self.supplier_stages = Counter()
        self.last_attempt_by_body = {}

    def timing_begin(self, year):
        self._year_start[year] = perf_counter()

    def timing_end(self, year):
        self.year_seconds[year] = perf_counter() - self._year_start.pop(year)

    def limits(self):
        limits = super().limits()
        limits.update(PR3B_SETTINGS)
        limits['BODY_COUNT'] = self.body_count
        limits['BODY_SELECTION_ORDER'] = self.bodies
        limits['SPONSOR_CLAIM_ORDER'] = ORDER
        limits['EXECUTOR_CAPACITY_CAP'] = None
        limits['PRIMARY_BLOCKER_ORDER'] = tuple(
            b for b in limits['PRIMARY_BLOCKER_ORDER']
            if b != 'MAX_NEW_STAGES_PER_SPONSOR_YEAR')
        limits['AUTHORED_ACTIVITY_IDS'] = AUTHORING
        limits['ACCESS_UNKNOWN_BODIES'] = tuple(
            b for b in self.bodies if REFERENCE_STATUS[b] == 'UNKNOWN')
        return limits

    def next_candidate(self, sponsor, excluded=frozenset()):
        # A claimant's reviewed A2 takes priority; one active claimant/body.
        for body in self.bodies:
            if (self.claims.get(body) == sponsor and body in self.reviews
                and self.reviews[body]['review'] == 'ADVANCE'
                and (body, 'A2') not in self.stages and
                    (body, 'A2') not in excluded):
                return body, 'A2'
        for body in self.bodies:
            if (body not in self.claims and body not in self.completed
                and (body, 'A1') not in excluded
                and self.last_a1_year.get(body, 0) < self.current_year):
                return body, 'A1'
        return None

    def attempt(self, k, sponsor, body, stage, year, used=0):
        attempt = self.a1_counts[body] + 1 if stage == 'A1' else 1
        # The failure fixture applies to one paid attempt, not all future retries.
        self.failures = frozenset({(body, stage)}
            if (body, stage, attempt) in self.injected_failures else ())
        row = super().attempt(k, sponsor, body, stage, year, used)
        self.failures = frozenset()
        row['study_attempt'] = attempt
        row['source_basis'] = ('AUTHORED_6C_TEST_ONLY' if body in AUTHORING
                               else 'GENERATED_TEST_ONLY')
        row['accessibility_status'] = REFERENCE_STATUS[body]
        if row['outcome'] == 'FUNDED':
            receipt = self.receipts[-1]
            receipt.update(study_attempt=attempt,
                           source_basis=row['source_basis'],
                           accessibility_status=REFERENCE_STATUS[body])
            if stage == 'A1':
                self.a1_counts[body] = attempt
                self.last_a1_year[body] = year
                self.reviews.pop(body, None)
            else:
                self.completed.add(body)
            self.pending.append(receipt)
            self.supplier_spend[year, sponsor] += D(receipt['amount'])
            self.supplier_stages[year, sponsor] += 1
            k.audit('BUILD8_PR3B_PAID_ATTEMPT_IDENTITY', year,
                    body=body, stage=stage, attempt=attempt,
                    disbursement_id=receipt['disbursement_id'],
                    source_basis=receipt['source_basis'],
                    classification='TEST_ONLY_NON_CANON')
        return row

    def review_completed(self, k, year):
        for prior in list(self.pending):
            if prior['year'] + SETTINGS['STUDY_DURATION_YEARS'] > year:
                continue
            self.pending.remove(prior)
            receipt_id = prior['disbursement_id']
            if receipt_id in self.reviewed_receipts:
                raise AssertionError('duplicate paid study review')
            self.reviewed_receipts.add(receipt_id)
            body, stage, attempt = (
                prior['body'], prior['stage'], prior['study_attempt'])
            authored = body in AUTHORING
            if prior['delivery'] == 'FAILED':
                result, draw = 'NO_RESULT', None
            elif authored:
                aid = AUTHORING[body][0 if stage == 'A1' else 1]
                result = self.portfolio.activity(aid).result_standing.value
                draw = None
            elif stage == 'A1':
                draw = review_draw(body, attempt)
                result = ('SUPPORTS_ADVANCE' if draw <
                          D(SETTINGS['A1_POSITIVE_REVIEW_FRACTION'])
                          else 'INSUFFICIENT')
            else:
                result, draw = 'STAGE_COMPLETE_NO_A3', None
            decision = ('ADVANCE' if result == 'SUPPORTS_ADVANCE' else
                        'CLOSED_NO_A3' if stage == 'A2' else 'HOLD')
            oid = (f'route1:pr3b:observation:{body}:{stage}:'
                   f'{attempt}:{prior["sponsor"]}:{prior["year"]}'
                   if result != 'NO_RESULT' and stage == 'A1' else None)
            ref = (f'BUILD8_PR3B_TEST_ONLY:{body}:{stage}:'
                   f'{attempt}:{prior["year"]}' if oid else None)
            record = dict(year=year, body=body, sponsor=prior['sponsor'],
                          study_year=prior['year'], stage=stage, attempt=attempt,
                          disbursement_id=receipt_id, result=result, review=decision,
                          draw=None if draw is None else str(draw),
                          source_basis=prior['source_basis'],
                          authored_activity=(AUTHORING[body][0 if stage=='A1' else 1]
                                             if authored else None),
                          observation_id=oid, result_ref=ref,
                          classification='TEST_ONLY_NOT_SCIENTIFIC_EVIDENCE')
            k.audit('BUILD8_PR3B_STUDY_RESULT', year, **{
                key: val for key, val in record.items() if key != 'year'})
            if oid:
                k.observations[oid] = Observation(
                    oid, year, prior['sponsor'], body + '-A1', ref, result, False)
                k.agents[prior['sponsor']].information.add(oid)
            if stage == 'A1':
                self.reviews[body] = record
                if result in PR3B_SETTINGS['A1_REOPEN_ON']:
                    self.claims.pop(body, None)
                    k.audit('BUILD8_PR3B_REOPEN_A1', year, body=body,
                            former_claimant=prior['sponsor'], attempt=attempt,
                            reason=result, classification='TEST_ONLY')
            self.studies.append(record)

    def record_states(self, year):
        for body in self.bodies:
            if year < SETTINGS['CAMPAIGN_START_YEAR']:
                status = 'HISTORICAL_BASELINE_UNCHANGED'
            elif body in self.completed:
                status = ('A2_AWAIT_REVIEW' if any(r['body'] == body and
                          r['stage'] == 'A2' for r in self.pending)
                          else 'A2_COMPLETE_NO_A3')
            elif body in self.claims:
                status = ('A2_READY' if body in self.reviews and
                          self.reviews[body]['review'] == 'ADVANCE'
                          else 'A1_AWAIT_REVIEW')
            elif self.a1_counts[body] > 0:
                status = 'A1_REOPENED'
            else:
                status = 'A1_AVAILABLE_UNFUNDED'
            self.body_yearly.append(dict(
                year=year, body=body, status=status,
                accessibility=('ACCESS_UNKNOWN' if REFERENCE_STATUS[body] == 'UNKNOWN'
                               else 'DERIVABLE_NOT_PHYSICAL_ROUTE'),
                source_basis=('AUTHORED_6C_TEST_ONLY' if body in AUTHORING
                              else 'GENERATED_TEST_ONLY'),
                a1_paid_attempts=self.a1_counts[body],
                claimant=self.claims.get(body)))

    def on_year(self, year, k, rows):
        self.current_year = year
        if year < SETTINGS['CAMPAIGN_START_YEAR']:
            self.record_states(year)
            return
        self.review_completed(k, year)
        started = len(self.attempts)
        # Each round lets every requester win at most one offer; no artificial
        # total, project, sponsor/year, executor, or retry limit is applied.
        considered = {s: set() for s in self.requesters}
        funded = Counter()
        while True:
            progress = False
            for sponsor in self.requesters:
                while True:
                    candidate = self.next_candidate(sponsor, considered[sponsor])
                    if candidate is None:
                        break
                    considered[sponsor].add(candidate)
                    event = self.attempt(k, sponsor, *candidate, year)
                    if event['outcome'] == 'FUNDED':
                        funded[sponsor] += 1
                        progress = True
                        break
            if not progress:
                break
        for row in rows:
            sponsor = row['sponsor']
            spend = self.supplier_spend[year, sponsor]
            row['campaign_spend'] = str(spend)
            row['campaign_stages'] = funded[sponsor]
            row['closing'] = str(k.state.accounts['route1:budget:' + sponsor].balance)
            if abs(D(row['opening']) + D(row['allocated']) - spend -
                   D(row['closing'])) > D('1e-24'):
                raise AssertionError('PR3B yearly sponsor conservation')
        today = self.attempts[started:]
        funded_count = sum(r['outcome'] == 'FUNDED' for r in today)
        assert len(today) == funded_count + sum(
            r['outcome'] == 'BLOCKED' and r['primary_blocker'] is not None
            for r in today)
        self.annual.append(dict(
            year=year, attempted=len(today), funded=funded_count,
            closing=str(sum((k.state.accounts['route1:budget:' + s].balance
                             for s in SPONSORS), D(0)))))
        self.record_states(year)

    def report(self):
        base = super().report()
        decade_times = tuple(dict(
            period=f'{y}-{min(y+9,2226)}',
            seconds=round(sum(self.year_seconds.get(z, 0) for z in range(
                y, min(y+9,2226)+1)), 6))
            for y in range(2026, 2227, 10))
        base.update(
            body_count=len(self.bodies), eligible_body_ids=self.bodies,
            body_yearly=tuple(self.body_yearly),
            source_standings={body: tuple(self.portfolio.activity(aid).result_standing.value
                               for aid in ids) for body, ids in AUTHORING.items()},
            accessibility={body: ('ACCESS_UNKNOWN' if REFERENCE_STATUS[body]=='UNKNOWN'
                                   else 'DERIVABLE_NOT_PHYSICAL_ROUTE')
                           for body in self.bodies},
            a1_attempt_counts=dict(sorted(self.a1_counts.items())),
            runtime_decades=decade_times,
            runtime_years=len(self.year_seconds),
            reopened_bodies=tuple(sorted(body for body, n in self.a1_counts.items()
                                         if n > 1)))
        assert len(base['body_yearly']) == 201 * len(self.bodies)
        assert len(self.year_seconds) == 201
        return base


def run_all_body_campaign(*, body_count=90, ceilings_enabled=True,
                          participating_sponsors=None, failures=(), root=None):
    from .route1_cast_payments import run_cast_payments
    campaign = AllBodyCampaign(body_count=body_count,
                               ceilings_enabled=ceilings_enabled,
                               participating_sponsors=participating_sponsors,
                               failures=failures)
    campaign.record_states(2026)
    start = perf_counter()
    result = run_cast_payments(end_year=2226, root=root, campaign_trial=campaign)
    duration = perf_counter() - start
    study_paid = {(r['year'], r['executor']) for r in campaign.receipts}
    result['executor_yearly'] = tuple(
        dict(row, status=('PAID_TEST_ONLY_STUDY'
                          if (row['year'], row['executor']) in study_paid
                          else row['status']))
        for row in result['executor_yearly'])
    result['campaign'] = campaign.report()
    result['campaign']['runtime_total_seconds'] = round(duration, 6)
    return result
