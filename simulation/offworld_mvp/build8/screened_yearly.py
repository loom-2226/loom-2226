"""Isolated Build 8 yearly screened checkpoint; legacy run_screened untouched."""
from decimal import Decimal as D
from hashlib import sha256
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import AgentState, AgentKind, ActionKind, BODY_MATERIAL_FAMILIES
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel.prospecting import SponsorProspectingRequest
from offworld_kernel.policy_runner import run_sponsor_prospecting_policy, run_financier_policy
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.policies.manifest import test_only_manifest
from .four_usa_financier import UNDERWRITING, SEED
from .opening import build_country_opening, EARTH_V4_ROOT
from .deliverable_chain import OPERATORS
from .competitive_delivery import SCALE, Work
from .trial_knowledge import record, terms, outcome as record_outcome
from .master_cast import name as cast_name, actor as cast_actor
from .yearly_selections import select as cast_selection

# Explicitly different, observable project underwriting, not sponsor-name belief.
CONTRACTS = ('FULL_ON_FAILURE', 'ACCEPTANCE_HOLDBACK')

# Scenario selection, not a global contractor pairing. Each legal identity and
# offered service is checked against the cast; price/timing stay authored here.
SUBCONTRACT_SELECTION = ('BUILD', 'LAND')

def eligible_subcontract_parties(prime_category='BUILD', sub_category='LAND', operators=None):
    operators = OPERATORS if operators is None else operators
    if prime_category == sub_category:
        raise ValueError('subcontract requires distinct service categories')
    if prime_category not in operators or sub_category not in operators:
        raise ValueError('unknown subcontract category')
    prime = cast_name(operators[prime_category][0], 'executor', prime_category)
    sub = cast_name(operators[sub_category][0], 'executor', sub_category)
    if prime == sub:
        raise ValueError('prime and sub must be distinct legal actors')
    return prime, sub



def run_yearly(order=None, root=EARTH_V4_ROOT, failure=None,
                 contract='FULL_ON_FAILURE', capacity_slots=2,
                 private_signal='NEGATIVE', share_private=False, immediate_funding=False,
                 subcontract=False, sub_failure=False, resource_on_failure=False,
                 operator_selection=None, selection='legacy_usa'):
    chosen = cast_selection(selection)
    sponsors = tuple(chosen['sponsors'])
    country = chosen['country']
    home = 'EARTH:'+country
    motives = chosen['motives']
    private_owner = chosen['private_observer']
    private_recipient = chosen['private_recipient']
    selected = {category: (chosen['executors'][category], *OPERATORS[category][1:])
                for category in ('BUILD', 'LAND')}
    for category, cost in chosen.get('authored_costs', {}).items():
        operator, _, markup, duration, slots = selected[category]
        selected[category] = (operator, cost, markup, duration, slots)
    if operator_selection is not None:
        for category, operator in operator_selection.items():
            if category not in ('BUILD', 'LAND'):
                raise ValueError('screened delivery only supports BUILD/LAND overrides')
            selected[category] = (cast_name(operator, 'executor', category), *selected[category][1:])
    if (sub_failure or resource_on_failure) and not subcontract:
        raise ValueError('subcontract failure/re-source requires subcontract')
    if contract not in CONTRACTS or capacity_slots not in (1,2):
        raise ValueError('invalid contract/capacity')
    if order is None:
        order = sponsors
    if set(order) != set(sponsors) or len(order) != len(sponsors):
        raise ValueError('order must contain each selected sponsor once')
    k,h,capacities,_ = build_country_opening(root)
    mobilization=k.mobilize_country_capital(1,country,capacities[country,2026],D(1),
        h['prospecting_scenario'],'b8_source:'+country,'b8_funds:'+country)
    amount=sum((SCALE*selected[c][1]*(1+selected[c][2]) for c in ('BUILD','LAND')),D(0))
    # Constrained: 2.00 clears one project. Immediate counterfactual:
    # 4.00 clears both. Both use mobilized country capital.
    # The 2/4 model-unit ceilings are AUTHORED, never national budget facts.
    # For other countries the available envelope cannot exceed actual mobilization.
    ceiling = D('4.00') if immediate_funding else D('2.00')
    fund = ceiling if selection == 'legacy_usa' else min(ceiling, mobilization.mobilized_cash)
    # One kernel generates the evidence and makes the economic decisions.
    # Public observations are synthetic; private truth is scenario-authored.
    posterior={}
    if (selection == 'legacy_usa' and (fund < amount or (not immediate_funding and fund >= 2*amount))) or fund <= 0 or fund > mobilization.mobilized_cash:
        raise ValueError('authored financing envelope inconsistent')
    k.add_account('screen:fund',country+'_SCREENED_FINANCIER',home,AccountKind.FUNDS)
    k.transfer(1,'b8_funds:'+country,'screen:fund',fund,TxPurpose.OTHER_INVESTMENT,
               parent_ids=(mobilization.transaction_id,))
    k.add_agent(AgentState('SCREEN_FINANCIER',AgentKind.PRIVATE_FINANCIER,home,
                           'screen:fund',{'FINANCE'},('RETURN',),priors={'resource_exists:'+f+'_PRESENT':D('.5') for f in BODY_MATERIAL_FAMILIES}))
    keys=tuple('BODY:MOON:'+f+'_PRESENT' for f in BODY_MATERIAL_FAMILIES)
    public,_,_=k.explore_paid(1,'PUB','','','earth_supplier',D(0),channel='REMOTE',
        public=False,false_positive=D(0),false_negative=D(0),update_belief=False,
        body_id='MOON',question_ref='BODY_MATERIAL_CHARACTERIZATION',
        body_truth={family:True for family in BODY_MATERIAL_FAMILIES})
    observation_ids=tuple(o.id for o in public)
    for obs in public:
        record(k,2026,obs.id,'PUB','OBSERVED',obs.question_ref+':'+obs.signal)
        k.publish_observation(1,'PUB',obs.id,'SCREENED_FINANCIER_DISCLOSURE',
            (('SCREEN_FINANCIER','resource_exists:'+obs.question_ref,D('.8'),D('.2')),))
        record(k,2026,obs.id,'SCREEN_FINANCIER','PUBLISHED','PUB')
    requests={}; sponsor_decisions={}; screenings={}
    for name in sorted(sponsors):
        motive,info=motives[name]
        k.add_account('screen:sponsor:'+name,name,home,AccountKind.FUNDS)
        k.add_node('screen:moon:'+name,NodeKind.OFFWORLD)
        k.add_account('screen:cash:'+name,name,'screen:moon:'+name,AccountKind.PROJECT_CASH)
        k.add_project('screen:project:'+name,'screen:moon:'+name,'screen:cash:'+name,{name:D(1)})
        k.add_agent(AgentState(name,AgentKind.PRIVATE_SPONSOR,home,
            'screen:sponsor:'+name,({'REQUEST_FINANCE','DEVELOP','EXPLORE'} if name==private_owner else {'REQUEST_FINANCE','DEVELOP'}),("RETURN",motive),
            priors={key:D('.5') for key in keys}))
        for obs in public:
            key='BODY:MOON:'+obs.question_ref
            k.publish_observation(1,'PUB',obs.id,'SCREENED_SPONSOR_DISCLOSURE',
                ((name,key,D('.8'),D('.2')),))
            record(k,2026,obs.id,name,'PUBLISHED','PUB')
        req=SponsorProspectingRequest('screen:opportunity:'+name,1,name,'screen:op:'+name,
            'screen:project:'+name,'MOON','REG','LOC',observation_ids,keys,amount,info).validate_protocol()
        snap=DecisionSnapshot(name,'PRIVATE_SPONSOR',home,'screen:sponsor:snapshot:'+name,
            '1',D(0),('REQUEST_FINANCE',),("RETURN",motive),observation_ids,tuple((key,D('.8')) for key in keys),
            tuple((key,D('.5')) for key in keys),(),(),(),(
                SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,str(amount),'AUTHORED'),
                SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,str(info),'AUTHORED'),
                SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,str(fund),'ACTUAL_FINANCIER_ENVELOPE')))
        sd=run_sponsor_prospecting_policy(snap,req,'screen:sponsor:decision:'+name).decision
        sponsor_decisions[name]=sd
        if sd.outcome.value!='INITIATE_PROJECT':
            continue
        financing=build_financing_request('screen:finance:'+name,1,name,
            'screen:project:'+name,amount,'DEVELOPMENT',observation_ids)
        requests[name]=financing
        k.submit_financing_request(financing)
    private,_,_=k.explore_paid(2,private_owner,'','','earth_supplier',D(0),channel='REMOTE',
        public=False,false_positive=D(0),false_negative=D(0),update_belief=False,
        body_id='MOON',question_ref='WATER_BEARING_MATERIAL_PRESENT',
        body_truth=(private_signal=='POSITIVE'))
    if private.signal!=private_signal:
        raise AssertionError('private signal mismatch')
    record(k,2026,private.id,private_owner,'OBSERVED',private.question_ref+':'+private.signal)
    if share_private:
        k.publish_observation(2,private_owner,private.id,'SCREENED_SHARED',
            ((private_recipient,'BODY:MOON:VOLATILES_PRESENT',D('.8'),D('.2')),))
        record(k,2026,private.id,private_recipient,'PUBLISHED',private_owner)
    k.publish_observation(2,private_owner,private.id,'SCREENED_PRIVATE',
        ((private_owner,'BODY:MOON:VOLATILES_PRESENT',D('.8'),D('.2')),))
    # The private observation updates volatile belief by an explicitly authored
    # relevance assumption; no other agent receives its raw contents.
    posterior={name:k.agents[name].beliefs['BODY:MOON:VOLATILES_PRESENT'] for name in sponsors}
    frozen=k.state.accounts['screen:fund'].balance
    manifest=test_only_manifest()
    for name,req in sorted(requests.items()):
        motive,info=motives[name]
        record(k,2026,'belief:VOLATILES:'+name,'SCREEN_FINANCIER','DISCLOSED',name)
        # Frozen underwriting snapshots before any allocation.
        snap=DecisionSnapshot('SCREEN_FINANCIER','PRIVATE_FINANCIER',home,
            'screen:finance:snapshot:'+name,'1',frozen,('FINANCE',),('RETURN',),observation_ids,
            (('resource_exists',posterior[name]),),(('resource_exists',D('.5')) ,),(),(),(),
            tuple(SnapshotFact(key,FactState.KNOWN,
                 ('0' if key=='underwriting.EXPLORATION_CAPEX' else str(amount) if key=='underwriting.DEVELOPMENT_CAPEX' else value),
                 'TEST_ONLY:PROJECT_EXECUTOR_BUDGET') for key,value in UNDERWRITING)+
            (SnapshotFact('capital.STRATEGIC_PRESSURE',FactState.KNOWN,
                          str(mobilization.strategic_pressure),'BUILD8_MOBILIZATION'),))
        execution=run_financier_policy(snap,req,manifest,'screen:finance:decision:'+name,
                                       allow_test_fixture=True)
        score=D(dict(execution.metrics)['annual_return_proxy']) if execution.decision.outcome.value=='APPROVE' else None
        # Pressure is reported separately; the existing financier policy does not
        # price pressure into return. No invented weighting is introduced.
        pressure=mobilization.strategic_pressure
        screenings[name]=(execution.decision,score,pressure)
        k.audit('BUILD8_EVIDENCE_BASIS',2026,sponsor=name,posterior=posterior[name],
                private_signal=private.signal,shared=share_private,
                cost_basis=amount,forecast_error=D(0))
    ranked=sorted((n for n,(d,s,p) in screenings.items() if d.outcome.value=='APPROVE'),
                  key=lambda n:(-screenings[n][1],sha256(f'{SEED}|1|screen:finance:{n}'.encode()).hexdigest()))
    # Calendar execution: reserve on start, settle and publish only on completion.
    approvals={}; pending=set(ranked); occupied={}; ready={}; stages={}
    active=[]; planned=[]
    for name in ranked:
        k.audit('BUILD8_FINANCE_SCREEN',2026,sponsor=name,decision=screenings[name][0].id,
                economic_score=screenings[name][1],pressure=screenings[name][2],
                pressure_contribution=D(0),outcome='APPROVED_AWAITING_CLEARING')
    for category in ('BUILD','LAND'):
        operator=cast_name(selected[category][0], 'executor', category)
        k.add_account('screen:revenue:'+category,operator,home,AccountKind.SUPPLIER)
        k.add_account('screen:expense:'+category,operator+' COST',home,AccountKind.SUPPLIER)
    rank={name:i for i,name in enumerate(ranked)}
    for year in range(2026,2035):
        if year==2027 and pending and not immediate_funding:
            extra=k.mobilize_country_capital(2,country,capacities[country,2027],D(1),
                h['prospecting_scenario'],'b8_source:'+country,'b8_funds:'+country)
            topup=min(amount,k.state.accounts['b8_funds:'+country].balance)
            k.transfer(2,'b8_funds:'+country,'screen:fund',topup,TxPurpose.OTHER_INVESTMENT,
                       parent_ids=(extra.transaction_id,))
        if year in (2026,2027):
            for name in ranked:
                if name not in pending or k.state.accounts['screen:fund'].balance<amount:
                    continue
                decision,score,pressure=screenings[name]
                k.financing_decisions[decision.id]=decision
                k.event(year-2025,'SCREEN_FINANCIER',ActionKind.FINANCE,'APPROVED',
                        (decision.id,decision.request_id,str(score)))
                k.transfer(year-2025,'screen:fund','screen:sponsor:'+name,amount,
                           TxPurpose.OTHER_INVESTMENT,parent_ids=(decision.id,))
                k.add_commitment('screen:commit:'+name,name,'screen:project:'+name,amount)
                k.disburse(year-2025,'screen:commit:'+name,'screen:sponsor:'+name,amount)
                k.transition_project_status(year-2025,name,'screen:project:'+name,'DEVELOPMENT',
                                            sponsor_decisions[name].id)
                approvals[name]=year
                record_outcome(k,year,name,'FUNDED',(name,'SCREEN_FINANCIER'),str(amount))
                terms(k,year,name,(name,'SCREEN_FINANCIER'),'FINANCE:'+str(amount)+':'+str(year))
                k.audit('BUILD8_FINANCE_CLEARING',year,sponsor=name,decision=decision.id,
                        outcome='FUNDED',amount=amount,economic_score=score,pressure=pressure,
                        pressure_contribution=D(0))
                ready[name]=year
                stages[name]=0
                pending.remove(name)
            for name in sorted(pending):
                record_outcome(k,year,name,'DEFERRED',(name,'SCREEN_FINANCIER'),'INSUFFICIENT_CASH')
                k.audit('BUILD8_FINANCE_CLEARING',year,sponsor=name,
                        decision=screenings[name][0].id,outcome='DEFERRED_INSUFFICIENT_CASH',
                        amount=amount,economic_score=screenings[name][1],
                        pressure=screenings[name][2],pressure_contribution=D(0))
        for job in sorted((j for j in active if j['finish']==year),key=lambda j:(rank[j['project']],j['category'])):
            name=job['project']; category=job['category']; index=stages[name]
            _,base,markup,duration,slots=selected[category]
            consumed=('COMMISSION:' if index==0 else 'BUILT:')+name
            cost=base*SCALE; price=cost*(1+markup)
            stage_outcome='FAILED' if failure==(name,category) or (job['sub'] is not None and sub_failure and not resource_on_failure) else 'DELIVERED'
            record_outcome(k,year,name,stage_outcome,(name,selected[category][0]),category)
            paid=price if stage_outcome=='DELIVERED' or contract=='FULL_ON_FAILURE' else price*D('.90')
            tx=k.transfer(year-2025,'screen:cash:'+name,'screen:revenue:'+category,
                          paid,TxPurpose.CAPEX,parent_ids=(screenings[name][0].id,consumed))
            if paid<cost: raise ValueError('contract requires executor working capital')
            if job['sub'] is not None:
                prime,supplier,sub_start,sub_finish=job['sub']
                sub_cost=base*SCALE*D('.40')
                sub_paid=sub_cost*D('.90') if sub_failure else sub_cost
                sub_tx=k.transfer(year-2025,'screen:revenue:BUILD','screen:revenue:LAND',
                                  sub_paid,TxPurpose.OTHER_INVESTMENT,parent_ids=(tx.id,))
                k.audit('BUILD8_SUB_PAYMENT',year,project=name,prime=prime,sub=supplier,
                        amount=sub_paid,quoted=sub_cost,withheld=sub_cost-sub_paid,
                        outcome='FAILED' if sub_failure else 'DELIVERED',transaction_id=sub_tx.id)
                cost_remainder=cost-sub_cost
            else: cost_remainder=cost
            k.transfer(year-2025,'screen:revenue:'+category,'screen:expense:'+category,
                       cost_remainder,TxPurpose.OTHER_INVESTMENT,parent_ids=(tx.id,))
            produced=(('BUILT:' if index==0 else 'ON_MOON:')+name) if stage_outcome=='DELIVERED' else None
            k.audit('BUILD8_SCREENED_DELIVERY',year,project=name,category=category,
                    outcome=stage_outcome,consumed=consumed,produced=produced or '',
                    revenue=paid,cost=cost,profit=paid-cost,contract=contract,withheld=price-paid)
            job['work']=Work(name,category,job['start'],year,stage_outcome,consumed,produced,paid,cost,paid-cost)
            ready[name]=year
            stages[name]+=1
        active=[j for j in active if j['finish']>year]
        for job in sorted((j for j in planned if j['sub'] is not None and j['sub'][3]==year),
                          key=lambda j:(rank[j['project']],j['category'])):
            if sub_failure and resource_on_failure:
                k.audit('BUILD8_SUB_RESOURCED',year,project=job['project'],prime=job['sub'][0],
                        route='PRIME_SELF_PERFORMS',new_finish=job['finish'])
        for name in sorted(stages,key=lambda n:(ready[n],rank[n])):
            if ready[name]>year or stages[name]>=2 or any(j['project']==name for j in active):
                continue
            index=stages[name]; category=('BUILD','LAND')[index]
            _,base,markup,duration,slots=selected[category]
            start=year
            while any(occupied.get((category,y),0)>=capacity_slots for y in range(start,start+duration)):
                start+=1
            if start>year:
                continue
            finish=start+duration
            sub=None
            if subcontract and category=='BUILD':
                prime,supplier=eligible_subcontract_parties(*SUBCONTRACT_SELECTION,operators=selected)
                sub_start=start
                while occupied.get(('LAND',sub_start),0)>=capacity_slots:
                    sub_start+=1
                sub_finish=sub_start+1
                occupied['LAND',sub_start]=occupied.get(('LAND',sub_start),0)+1
                finish=max(finish,sub_finish)
                if sub_failure and resource_on_failure:
                    finish=max(finish,sub_finish)+1
                sub=(prime,supplier,sub_start,sub_finish)
            for y in range(start,finish):
                occupied[category,y]=occupied.get((category,y),0)+1
            consumed=('COMMISSION:' if index==0 else 'BUILT:')+name
            if index==1 and not any(j.get('work') and j['project']==name and j['work'].produced==consumed for j in planned):
                record_outcome(k,year,name,'BLOCKED_UPSTREAM',(name,),category)
                planned.append({'project':name,'category':category,'start':year,'finish':year,'sub':None,
                                'work':Work(name,category,year,year,'BLOCKED_UPSTREAM',consumed,None,D(0),D(0),D(0))})
                stages[name]=2
                continue
            cast_actor(selected[category][0],'executor',category)
            cost=base*SCALE;price=cost*(1+markup)
            terms(k,start,name,(name,selected[category][0]),category+':'+str(price)+':'+contract)
            if sub is not None:
                prime,supplier,sub_start,sub_finish=sub
                fact='subcontract:'+name+':BUILD:'+prime+':'+supplier
                # Contract knowledge is learned at the subcontract start, not at completion.
                record(k,sub_start,fact,prime,'DIRECT_CONTRACT',supplier)
                record(k,sub_start,fact,supplier,'DIRECT_CONTRACT',prime)
                k.audit('BUILD8_SUBCONTRACT',sub_start,project=name,prime=prime,sub=supplier,
                        start=sub_start,finish=sub_finish,price=base*SCALE*D('.40'),
                        outcome='FAILED' if sub_failure else 'DELIVERED',depth=1)
            job={'project':name,'category':category,'start':start,'finish':finish,'sub':sub}
            active.append(job);planned.append(job)
    k.assert_invariants()
    work=tuple(sorted((j['work'] for j in planned if 'work' in j),
                      key=lambda w:(w.start,rank[w.project],w.category)))
    decisions=tuple((n,sponsor_decisions[n].outcome.value,
                     screenings[n][0].outcome.value if n in screenings else 'NOT_REQUESTED',
                     str(screenings[n][1]) if n in screenings else '',approvals.get(n)) for n in sponsors)
    return work,decisions,k,occupied
