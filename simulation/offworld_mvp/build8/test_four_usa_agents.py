"""Noncanon: four named private USA Agents compete for one Earth-v4-backed pool."""
import unittest
from decimal import Decimal as D
from offworld_kernel.model import AccountKind, TxPurpose
from offworld_kernel.mvp_state import AgentState, AgentKind, BODY_MATERIAL_FAMILIES
from offworld_kernel.prospecting import SponsorProspectingRequest
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel import policy_runner
from .opening import build_country_opening
from .two_economy_source_finance_trial import ROOT
from .sponsor_executor_network_trial import PRIVATE

NAMES=('SpaceX','Blue Origin','Interlune','Axiom')
KEYS=tuple('BODY:MOON:'+f+'_PRESENT' for f in BODY_MATERIAL_FAMILIES)
KEY='BODY:MOON:VOLATILES_PRESENT'

def trial(private_positive=False, order=NAMES, financier_clearing=False, disclose_private=True):
    if len(order)!=len(NAMES) or set(order)!=set(NAMES):
        raise ValueError("order must be a permutation of four USA Sponsors")
    k,h,capacities,_=build_country_opening(ROOT)
    assert all('USA' in PRIVATE[n] for n in NAMES)
    rec=k.mobilize_country_capital(1,'USA',capacities['USA',2026],D(1),h['prospecting_scenario'],'b8_source:USA','b8_funds:USA')
    # Bounded authored experiment budget is drawn from the actual mobilized USA pool.
    budget=D('.50'); cost=D('.25')
    assert rec.mobilized_cash>=budget
    k.add_account('usa:trial:pool','USA:FOUR_SPONSOR_TRIAL','EARTH:USA',AccountKind.FUNDS)
    k.transfer(1,'b8_funds:USA','usa:trial:pool',budget,TxPurpose.OTHER_INVESTMENT,parent_ids=(rec.transaction_id,))
    k.add_account('usa:trial:supplier','USA:SUPPLIER','EARTH:USA',AccountKind.SUPPLIER)
    for name in NAMES:
        k.add_account('usa:trial:fund:'+name,name,'EARTH:USA',AccountKind.FUNDS,D(0))
        k.add_account('usa:trial:cash:'+name,name,'EARTH:USA',AccountKind.PROJECT_CASH)
        k.add_project('usa:trial:project:'+name,'EARTH:USA','usa:trial:cash:'+name,{name:D(1)})
        k.add_agent(AgentState(name,AgentKind.PRIVATE_SPONSOR,'EARTH:USA','usa:trial:fund:'+name,
                               {'REQUEST_FINANCE','DEVELOP','EXPLORE'} if name=='SpaceX' else {'REQUEST_FINANCE','DEVELOP'},
                               ('RETURN',),priors={key:D('.5') for key in KEYS}))
    public,_,_=k.explore_paid(1,'PUB','','','usa:trial:supplier',D(0),channel='REMOTE',
        public=False,false_positive=D(0),false_negative=D(0),update_belief=False,
        body_id='MOON',question_ref='BODY_MATERIAL_CHARACTERIZATION',
        body_truth={family:True for family in BODY_MATERIAL_FAMILIES})
    for o in public:
        key='BODY:MOON:'+o.question_ref
        k.publish_observation(1,'PUB',o.id,'SYNTHETIC_USA_PUBLIC',
            tuple((name,key,D('.8') if key==KEY else D('.5'),D('.2') if key==KEY else D('.5')) for name in NAMES))
    private,_,_=k.explore_paid(2,'SpaceX','','','usa:trial:supplier',D(0),channel='REMOTE',
        public=False,false_positive=D(0),false_negative=D(0),update_belief=False,
        body_id='MOON',question_ref='WATER_BEARING_MATERIAL_PRESENT',body_truth=private_positive)
    expected='POSITIVE' if private_positive else 'NEGATIVE'
    assert private.signal==expected
    k.publish_observation(2,'SpaceX',private.id,'SYNTHETIC_USA_PRIVATE',(('SpaceX',KEY,D('.8'),D('.2')),))
    if financier_clearing:
        from .four_usa_financier import finance_requests
        return finance_requests(k,h,NAMES,order,public,private,private_positive,disclose_private,cost,budget,rec)
    results={}
    # Fixed priority is an experimental control, not a market allocation mechanism.
    for name in order:
        a=k.agents[name]
        ids=tuple(sorted(i for i in a.information if i in k.observations))
        req=SponsorProspectingRequest('usa:req:'+name,2,name,'usa:opp:'+name,'usa:trial:project:'+name,
            'MOON','REG','LOC',tuple(o.id for o in public),KEYS,cost,D('.39')).validate_protocol()
        snap=DecisionSnapshot(name,'PRIVATE_SPONSOR','EARTH:USA','usa:snap:'+name,'2',D(0),
            ('REQUEST_FINANCE',),('RETURN',),ids,
            tuple((key,a.beliefs[key]) for key in KEYS),tuple((key,a.priors[key]) for key in KEYS),(),(),(),(
                SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,str(cost),'SYNTHETIC'),
                SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,'.39','SYNTHETIC'),
                SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,'1','SYNTHETIC')))
        decision=policy_runner.run_sponsor_prospecting_policy(snap,req,'usa:decision:'+name).decision.outcome.value
        funded=decision=='INITIATE_PROJECT' and k.state.accounts['usa:trial:pool'].balance>=cost
        if funded:
            k.transfer(2,'usa:trial:pool','usa:trial:cash:'+name,cost,TxPurpose.OTHER_INVESTMENT,parent_ids=('usa:decision:'+name,))
            k.transition_project_status(2,name,'usa:trial:project:'+name,'DEVELOPMENT','usa:decision:'+name)
        elif decision=='DECLINE':
            k.transition_project_status(2,name,'usa:trial:project:'+name,'ABANDONED','usa:decision:'+name)
        results[name]=(str(a.beliefs[KEY]),decision,'FUNDED' if funded else 'DECLINED' if decision=='DECLINE' else 'UNFUNDED',k.state.projects['usa:trial:project:'+name].status)
    k.assert_invariants()
    assert sum(k.state.accounts['usa:trial:cash:'+n].balance for n in NAMES)+k.state.accounts['usa:trial:pool'].balance==budget
    return results,k.fingerprint(),str(rec.mobilized_cash),str(k.state.accounts['usa:trial:pool'].balance)

class FourUSAAgents(unittest.TestCase):
    def test_private_information_changes_anothers_funding(self):
        negative=trial(False);positive=trial(True)
        self.assertEqual(negative,trial(False))
        self.assertEqual(positive,trial(True))
        for name in NAMES[1:]:
            self.assertEqual(negative[0][name][0:2],positive[0][name][0:2])
        self.assertEqual(negative[0]['SpaceX'][1:3],('DECLINE','DECLINED'))
        self.assertEqual(positive[0]['SpaceX'][1:3],('INITIATE_PROJECT','FUNDED'))
        self.assertEqual(negative[0]['Interlune'][2],'FUNDED')
        self.assertEqual(positive[0]['Interlune'][2],'UNFUNDED')
        self.assertEqual(negative[0]['Blue Origin'][2],positive[0]['Blue Origin'][2])
        self.assertEqual(negative[3],positive[3])
        print('FOUR_USA_AGENTS',negative[0],positive[0],negative[2:])
