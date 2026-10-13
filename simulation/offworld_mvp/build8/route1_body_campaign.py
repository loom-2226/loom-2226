"""TEST_ONLY, NON-CANON 2036+ body-study spending on existing Route 1 accounts.

Paid studies are abstract supplier services, NOT spacecraft missions or genuine
scientific observations. The synthetic review never inspects generated WORLD.
"""
from collections import Counter
from decimal import Decimal as D
from hashlib import sha256
from offworld_kernel.model import AccountKind, TxPurpose
from offworld_kernel.mvp_state import Observation
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.policy import DecisionSnapshot, FactState, SnapshotFact
from offworld_kernel.policy_runner import run_financier_policy
from offworld_kernel.policies.manifest import test_only_manifest
from simulation.offworld_mvp.build6e.generated_world import load_inputs
from .master_cast import actor
from .route1_gate1 import CEILINGS, EVIDENCE, EVIDENCE_TAG
from .route1_cast_payments import EXTRA_CEILINGS, PREFERRED, SERVICES, available_quotes
from .sponsor_executor_network_trial import EXECUTORS, PUBLIC, PRIVATE

BODIES = ('EUROPA', 'PHOBOS')
HISTORICAL_BODIES = frozenset(('MOON', 'MARS', 'CERES', 'BENNU'))
SPONSORS = frozenset(PUBLIC) | frozenset(PRIVATE)
CEILING = {**CEILINGS, **EXTRA_CEILINGS}
ORDER = tuple(sorted(SPONSORS, key=lambda s: (
    actor(s, 'agency_sponsor' if s in PUBLIC else 'private_sponsor')['id'], s)))
# All potentially limiting authored settings; the financier's own public
# manifest is embedded in the effective register rather than overridden.
SETTINGS = {
    'CAMPAIGN_START_YEAR': 2036,
    'CAMPAIGN_END_YEAR': 2226,
    'MAX_NEW_STAGES_PER_SPONSOR_YEAR': 1,
    'MAX_CLAIMANTS_PER_BODY_CAMPAIGN': 1,
    'MAX_AUTHORED_STAGE': 'A2',
    'SPONSOR_CLAIM_ORDER': ORDER,
    'BODY_SELECTION_ORDER': tuple(sorted(BODIES)),
    'A1_POSITIVE_REVIEW_FRACTION': '0.50',
    'A1_REVIEW_SEED': 'ROUTE1_BODY_PR3A_V1',
    'STUDY_DURATION_YEARS': 1,
    'A1_SERVICE_CATEGORY': 'RUN',
    'A1_SERVICE_PRICE': SERVICES['RUN'][1],
    'A2_SERVICE_CATEGORY': 'BUILD',
    'A2_SERVICE_PRICE': SERVICES['BUILD'][1],
    'COUNTRY_ALLOCATION_SHARE': '0.25',
    'FINANCIER_RESOURCE_BELIEF': '0.5',
    'FINANCIER_RESOURCE_PRIOR': '0.5',
    'FINANCIER_UNDERWRITING_FACTS': dict(EVIDENCE),
    'A1_DISCLOSED_EVIDENCE_SOURCE': EVIDENCE_TAG,
    'SPONSOR_REQUEST_CEILINGS': CEILING,
    'LIFETIME_SPENDING_CAP': None,
    'CARRY_CAP': None,
    'GLOBAL_PROJECT_CAP': None,
    'EXECUTOR_CAPACITY_CAP': None,
}
BLOCK_ORDER = (
    'MAX_NEW_STAGES_PER_SPONSOR_YEAR',
    'MAX_CLAIMANTS_PER_BODY_CAMPAIGN', 'A1_REVIEW_NOT_READY',
    'A1_REVIEW_INSUFFICIENT', 'COMPARABLE_EXECUTOR_QUOTE',
    'EXECUTOR_CAPABILITY', 'SPONSOR_REQUEST_CEILINGS',
    'ACTUAL_SPONSOR_CASH', 'FINANCIER_CONCENTRATION',
    'FINANCIER_INFORMATION', 'FINANCIER_RETURN', 'FINANCIER_OTHER',
)
assert len(SPONSORS)==20 and len(EXECUTORS)==16 and set(CEILING)==SPONSORS


def a1_draw(body):
    """Uniform SHA256 replayable TEST_ONLY draw, unrelated to hidden truth."""
    key=f"{SETTINGS['A1_REVIEW_SEED']}|{body}|A1"
    return D(int.from_bytes(sha256(key.encode()).digest(), 'big')) / D(2**256)


def decade_counts(attempts):
    periods=[]
    for first in range(2036, 2227, 10):
        last=min(2226,first+9)
        group=[a for a in attempts if first<=a['year']<=last]
        failures=Counter(a['primary_blocker'] for a in group if a['outcome']!='FUNDED')
        funded=sum(a['outcome']=='FUNDED' for a in group)
        assert len(group)==funded+sum(failures.values())
        periods.append(dict(period=f'{first}-{last}',attempted=len(group),
                            funded=funded,blockers=dict(sorted(failures.items()))))
    return tuple(periods)


class BodyCampaign:
    def __init__(self, ceilings_enabled=True, participating_sponsors=None,
                 max_stages_per_year=None, failures=()):
        rows,_=load_inputs()
        if any(b not in rows or rows[b]['material_model_applicability'] not in
               ('SOLID','SOLID_WITH_ATMOSPHERE') for b in BODIES):
            raise ValueError('body not eligible for solid study')
        if set(BODIES)&HISTORICAL_BODIES:
            raise ValueError('historical body cannot receive generated duplicate chain')
        sponsors=SPONSORS if participating_sponsors is None else frozenset(participating_sponsors)
        if not sponsors or not sponsors<=SPONSORS:
            raise ValueError('invalid requesting sponsor set')
        self.requesters=tuple(s for s in ORDER if s in sponsors)
        self.max_stages=(SETTINGS['MAX_NEW_STAGES_PER_SPONSOR_YEAR']
                         if max_stages_per_year is None else max_stages_per_year)
        if type(self.max_stages) is not int or self.max_stages<1:
            raise ValueError('stage limit must be positive')
        self.ceilings_enabled=bool(ceilings_enabled)
        self.failures=frozenset(failures)
        if any(body not in BODIES or stage not in ('A1','A2') for body,stage in self.failures):
            raise ValueError('bad authored stage failure')
        self.claims={}
        self.stages={}
        self.reviews={}
        self.terminal_a2=set()
        self.attempts=[]
        self.receipts=[]
        self.studies=[]
        self.annual=[]
        self.manifest=test_only_manifest()
        self.quotes=available_quotes()

    def limits(self):
        result=dict(SETTINGS)
        result.update({
            'SPONSOR_REQUEST_CEILINGS_ENABLED': self.ceilings_enabled,
            'MAX_NEW_STAGES_PER_SPONSOR_YEAR': self.max_stages,
            'PARTICIPATING_SPONSORS': self.requesters,
            'TEST_ONLY_DELIVERY_FAILURES': tuple(sorted(self.failures)),
            'FINANCIER_POLICY': self.manifest.policy_id,
            'FINANCIER_SETTINGS': {p.semantic_name:str(p.value)
                                    for p in self.manifest.parameters},
            'FINANCIER_DISCLOSURE_REQUIRED': True,
            'FINANCIER_CASH_REQUIRED': True,
            'EXECUTOR_CAPABILITIES': {s:caps for s,(_,caps) in EXECUTORS.items()},
            'PRIMARY_BLOCKER_ORDER': BLOCK_ORDER,
            'CLASSIFICATION':'AUTHORED TEST_ONLY NON-CANON'})
        return result

    def quote(self,sponsor,category):
        bids=[]
        for executor,price in self.quotes.get(category,()):
            if category not in EXECUTORS[executor][1]:
                continue
            key=actor(executor,'executor',category)['id']
            bids.append((price,int(executor!=PREFERRED[sponsor]),key,executor))
        if not bids:
            return None
        price,_,_,executor=min(bids)
        return dict(executor=executor,price=price,
                    offers=len(bids),category=category)

    def review_completed_a1(self,k,year):
        for (body,stage),prior in sorted(self.stages.items()):
            if stage!='A1' or body in self.reviews:
                continue
            if prior['year']+SETTINGS['STUDY_DURATION_YEARS']>year:
                continue
            draw=a1_draw(body) if prior['delivery']=='DELIVERED' else None
            outcome=('NO_RESULT' if prior['delivery']=='FAILED' else
                     'SUPPORTS_ADVANCE' if draw is not None and
                     draw<D(SETTINGS['A1_POSITIVE_REVIEW_FRACTION'])
                     else 'INSUFFICIENT')
            decision='ADVANCE' if outcome=='SUPPORTS_ADVANCE' else 'HOLD'
            oid=f'route1:campaign:observation:{body}:A1:{prior["sponsor"]}'
            ref=f'BUILD8_TEST_ONLY_STUDY:{body}:A1:{prior["year"]}'
            record=dict(year=year,body=body,sponsor=prior['sponsor'],
                        stage='A1',study_year=prior['year'],
                        result=outcome,review=decision,
                        draw=None if draw is None else str(draw),
                        positive_threshold=SETTINGS['A1_POSITIVE_REVIEW_FRACTION'],
                        observation_id=oid,result_ref=ref,
                        classification='TEST_ONLY_SYNTHETIC_NOT_SCIENTIFIC_EVIDENCE')
            k.audit('BUILD8_CAMPAIGN_A1_RESULT',year,**{a:b for a,b in record.items() if a!='year'})
            if outcome!='NO_RESULT':
                k.observations[oid]=Observation(
                    oid,year,prior['sponsor'],body+'-A1',ref,outcome,False)
                k.agents[prior['sponsor']].information.add(oid)
            else:
                # Supplier failure earns no fabricated observational knowledge.
                record['observation_id']=None
                record['result_ref']=None
            k.audit('BUILD8_CAMPAIGN_A1_REVIEW',year,body=body,sponsor=prior['sponsor'],
                    result_ref=record['result_ref'],review=decision,classification='TEST_ONLY_NON_CANON')
            self.reviews[body]=record
            self.studies.append(record)

    def next_candidate(self,sponsor,excluded=frozenset()):
        # Existing claimant gets earned A2 first. Otherwise first unclaimed A1.
        for body in SETTINGS['BODY_SELECTION_ORDER']:
            if (self.claims.get(body)==sponsor and (body,'A2') not in self.stages
                and body in self.reviews and body not in self.terminal_a2
                and (body,'A2') not in excluded):
                return (body,'A2')
        for body in SETTINGS['BODY_SELECTION_ORDER']:
            if body not in self.claims and (body,'A1') not in excluded:
                return (body,'A1')
        return None

    def financier_decision(self,k,sponsor,body,stage,year,price):
        obs=(self.reviews[body]['observation_id'] if stage=='A2' else
             'route1:authored:observation:'+sponsor)
        project=f'route1:campaign:project:{body}:{sponsor}'
        rid=f'route1:campaign:request:{body}:{stage}:{sponsor}:{year}'
        request=build_financing_request(
            rid,year-2025,sponsor,project,price,'DEVELOPMENT',
            disclosed_observation_ids=(obs,))
        k.submit_financing_request(request)
        facts=tuple(SnapshotFact(key,FactState.KNOWN,v,EVIDENCE_TAG) for key,v in EVIDENCE)
        snap=DecisionSnapshot(
            'ROUTE1_FINANCIER','PRIVATE_FINANCIER',
            'EARTH:'+(PUBLIC[sponsor] if sponsor in PUBLIC else PRIVATE[sponsor])[0],
            f'route1:campaign:snapshot:{body}:{stage}:{sponsor}:{year}',
            str(year-2025),k.state.accounts['route1:budget:'+sponsor].balance,
            ('FINANCE',),('RETURN',),(obs,),
            (('resource_exists',D(SETTINGS['FINANCIER_RESOURCE_BELIEF'])),),
            (('resource_exists',D(SETTINGS['FINANCIER_RESOURCE_PRIOR'])),),
            (),(),(),facts)
        return run_financier_policy(
            snap,request,self.manifest,
            f'route1:campaign:decision:{body}:{stage}:{sponsor}:{year}',
            allow_test_fixture=True).decision

    def attempt(self,k,sponsor,body,stage,year,used):
        category=SETTINGS[stage+'_SERVICE_CATEGORY']
        price=D(SETTINGS[stage+'_SERVICE_PRICE'])
        balance=k.state.accounts['route1:budget:'+sponsor].balance
        ceiling=D(CEILING[sponsor])
        quote=self.quote(sponsor,category)
        blocker=policy_reason=None
        if self.max_stages is not None and used>=self.max_stages:
            blocker='MAX_NEW_STAGES_PER_SPONSOR_YEAR'
        elif stage=='A1' and body in self.claims:
            blocker='MAX_CLAIMANTS_PER_BODY_CAMPAIGN'
        elif stage=='A2' and body not in self.reviews:
            blocker='A1_REVIEW_NOT_READY'
        elif stage=='A2' and self.reviews[body]['review']!='ADVANCE':
            blocker='A1_REVIEW_INSUFFICIENT'
        elif quote is None:
            blocker='COMPARABLE_EXECUTOR_QUOTE'
        elif category not in EXECUTORS[quote['executor']][1]:
            blocker='EXECUTOR_CAPABILITY'
        elif self.ceilings_enabled and price>ceiling:
            blocker='SPONSOR_REQUEST_CEILINGS'
        elif price>balance:
            blocker='ACTUAL_SPONSOR_CASH'
        if blocker is None:
            # The existing financing protocol requires an identified project
            # before accepting a request; the zero-cash project is not a claim.
            project=f'route1:campaign:project:{body}:{sponsor}'
            if project not in k.state.projects:
                node='OFF:ROUTE1:'+sponsor
                cash=f'route1:campaign:cash:{body}:{sponsor}'
                k.add_account(cash,sponsor,node,AccountKind.PROJECT_CASH)
                k.add_project(project,node,cash,{sponsor:D(1)})
            dec=self.financier_decision(k,sponsor,body,stage,year,price)
            policy_reason=dec.reason_code.value
            if dec.outcome.value!='APPROVE':
                blocker={'CONCENTRATION':'FINANCIER_CONCENTRATION',
                         'DEFER_MORE_INFORMATION':'FINANCIER_INFORMATION',
                         'BELOW_RETURN':'FINANCIER_RETURN',
                         'CEILING':'ACTUAL_SPONSOR_CASH'}.get(
                             policy_reason,'FINANCIER_OTHER')
        row=dict(year=year,sponsor=sponsor,body=body,stage=stage,
                 category=category,amount=str(price),
                 balance_before=str(balance),ceiling=str(ceiling),
                 ceiling_enabled=self.ceilings_enabled,
                 executor=quote['executor'] if quote else None,
                 outcome='BLOCKED' if blocker else 'FUNDED',
                 primary_blocker=blocker,policy_reason=policy_reason,
                 named_stage_limit=self.max_stages,
                 classification='AUTHORED TEST_ONLY NON-CANON')
        if blocker is None:
            project=f'route1:campaign:project:{body}:{sponsor}'
            cash=f'route1:campaign:cash:{body}:{sponsor}'
            cid=f'route1:campaign:commit:{body}:{stage}:{sponsor}:{year}'
            k.add_commitment(cid,'ROUTE1_FINANCIER',project,price)
            tx=k.disburse(year,cid,'route1:budget:'+sponsor,price)
            supplier='route1:executor:'+quote['executor']
            if supplier not in k.state.accounts:
                k.add_account(supplier,quote['executor'],
                              'EARTH:'+EXECUTORS[quote['executor']][0],AccountKind.SUPPLIER)
            payment=k.transfer(year,cash,supplier,price,TxPurpose.CAPEX,
                               parent_ids=(tx.id,))
            if k.state.accounts[cash].balance!=0:
                raise AssertionError('campaign project cash not conserved')
            delivery='FAILED' if (body,stage) in self.failures else 'DELIVERED'
            receipt=dict(year=year,body=body,stage=stage,sponsor=sponsor,
                         executor=quote['executor'],category=category,
                         quote_count=quote['offers'],amount=str(price),
                         disbursement_id=tx.id,supplier_payment_id=payment.id,
                         delivery=delivery,
                         output=(f'BUILD8_TEST_ONLY_STUDY:{body}:{stage}:{year}'
                                 if delivery=='DELIVERED' else None),
                         physical_mission_claim=False)
            self.receipts.append(receipt)
            self.stages[body,stage]=receipt
            if stage=='A1':
                self.claims[body]=sponsor
            row.update(disbursement_id=tx.id,supplier_payment_id=payment.id)
            k.audit('BUILD8_CAMPAIGN_PAID_STUDY',year,
                    **{a:b for a,b in receipt.items() if a!='year'},
                    classification='TEST_ONLY_NON_CANON')
        self.attempts.append(row)
        if stage=='A2' and blocker=='A1_REVIEW_INSUFFICIENT':
            self.terminal_a2.add(body)
        k.audit('BUILD8_CAMPAIGN_REQUEST',year,
                **{a:b for a,b in row.items() if a!='year'})
        return row

    def on_year(self,year,k,rows):
        if year<SETTINGS['CAMPAIGN_START_YEAR'] or year>SETTINGS['CAMPAIGN_END_YEAR']:
            return
        self.review_completed_a1(k,year)
        funded=Counter()
        for sponsor in self.requesters:
            considered=set()
            while True:
                choice=self.next_candidate(sponsor,considered)
                if choice is None:
                    break
                body,stage=choice
                considered.add(choice)
                event=self.attempt(k,sponsor,body,stage,year,funded[sponsor])
                if event['outcome']=='FUNDED':
                    funded[sponsor]+=1
                    if funded[sponsor]>=self.max_stages:
                        other=self.next_candidate(sponsor,considered)
                        if other is not None:
                            self.attempt(k,sponsor,*other,year,funded[sponsor])
                        break
                else:
                    # Other body candidates may have different costs in future;
                    # no hidden global retry cap. The two-body prices are equal.
                    continue
        for row in rows:
            sponsor=row['sponsor']
            spend=sum((D(r['amount']) for r in self.receipts
                       if r['year']==year and r['sponsor']==sponsor),D(0))
            row['campaign_spend']=str(spend)
            row['campaign_stages']=funded[sponsor]
            row['closing']=str(k.state.accounts['route1:budget:'+sponsor].balance)
            if abs(D(row['opening'])+D(row['allocated'])-spend-
                   D(row['closing']))>D('1e-24'):
                raise AssertionError('annual campaign budget conservation')
        self.annual.append(dict(year=year,attempted=sum(r['year']==year for r in self.attempts),
                                funded=sum(r['year']==year and r['outcome']=='FUNDED'
                                           for r in self.attempts),
                                closing=str(sum((k.state.accounts[
                                    'route1:budget:'+s].balance for s in SPONSORS),D(0)))))

    def report(self):
        decades=decade_counts(self.attempts)
        assert sum(x['attempted'] for x in decades)==len(self.attempts)
        return dict(limits=self.limits(),claims=dict(sorted(self.claims.items())),
                    attempts=tuple(self.attempts),receipts=tuple(self.receipts),
                    studies=tuple(self.studies),decades=decades,
                    annual=tuple(self.annual),
                    no_a3=tuple(sorted(b for (b,s) in self.stages if s=='A2')))




def run_body_campaign(*, ceilings_enabled=True, participating_sponsors=None,
                      max_stages_per_year=None, failures=(), root=None):
    # Existing 201-year cast and cash ledger, only the new explicit opt-in hook.
    from .route1_cast_payments import run_cast_payments
    campaign=BodyCampaign(ceilings_enabled=ceilings_enabled,
                          participating_sponsors=participating_sponsors,
                          max_stages_per_year=max_stages_per_year,failures=failures)
    result=run_cast_payments(end_year=2226,root=root,
                             run_setting={'name':'two_body_campaign','campaign':campaign})
    result['campaign']=campaign.report()
    return result
