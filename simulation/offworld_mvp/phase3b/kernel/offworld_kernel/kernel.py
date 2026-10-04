from __future__ import annotations
from decimal import Decimal
from hashlib import sha256
import json
from .model import *

class InvariantError(RuntimeError): pass

class Kernel:
    '''Deterministic Phase 3B state kernel. No autonomous agent decisions.'''
    def __init__(self, state=None, lambda_displacement=D('1')):
        self.state=state or KernelState(); self.lambda_displacement=D(lambda_displacement); self._seq=0
    def _id(self,prefix): self._seq+=1; return f'{prefix}-{self._seq:06d}'
    def add_node(self,node_id,kind):
        if node_id in self.state.nodes: raise InvariantError(f'duplicate node {node_id}')
        self.state.nodes[node_id]=Node(node_id,kind)
    def add_account(self,account_id,owner_id,node_id,kind,balance=D('0')):
        if node_id not in self.state.nodes: raise InvariantError(f'unknown node {node_id}')
        if account_id in self.state.accounts: raise InvariantError(f'duplicate account {account_id}')
        self.state.accounts[account_id]=Account(account_id,owner_id,node_id,kind,D(balance))
    def add_project(self,project_id,node_id,cash_account_id,owners=None):
        if cash_account_id not in self.state.accounts: raise InvariantError('project cash account missing')
        if self.state.accounts[cash_account_id].node_id != node_id: raise InvariantError('project cash location mismatch')
        owners={k:D(v) for k,v in (owners or {}).items()}
        if owners and sum(owners.values(),D('0')) != D('1'): raise InvariantError('owner shares must sum to one')
        self.state.projects[project_id]=Project(project_id,node_id,cash_account_id,owners)
    def add_commitment(self,cid,financier_id,project_id,amount):
        amount=D(amount)
        if amount<0 or project_id not in self.state.projects: raise InvariantError('invalid commitment')
        self.state.commitments[cid]=Commitment(cid,financier_id,project_id,amount,amount)
    def _earth_shadow_add_currency(self,field,node_id,year,amount):
        ledger=getattr(self.state.earth_impact,field); key=(str(node_id),int(year))
        ledger[key]=ledger.get(key,D('0'))+D(amount)

    def _record_earth_shadow_transfer(self,tx):
        source_kind=self.state.nodes[tx.source_location].kind
        destination_kind=self.state.nodes[tx.destination_location].kind
        if source_kind==NodeKind.EARTH and destination_kind==NodeKind.OFFWORLD:
            if tx.purpose in {TxPurpose.DISBURSE,TxPurpose.PUBLIC_SUBSIDY,TxPurpose.OTHER_INVESTMENT}:
                self._earth_shadow_add_currency('capital_diverted_to_offworld',tx.source_location,tx.year,tx.amount)
        elif source_kind==NodeKind.OFFWORLD and destination_kind==NodeKind.EARTH:
            if tx.purpose in {TxPurpose.RETURN_TO_EARTH,TxPurpose.FINANCIER_RETURN,TxPurpose.OWNER_DISTRIBUTION}:
                self._earth_shadow_add_currency('capital_returned_to_earth',tx.destination_location,tx.year,tx.amount)
            elif tx.purpose in {TxPurpose.CAPEX,TxPurpose.EXPLORATION,TxPurpose.OPEX,TxPurpose.TRANSPORT_PAYMENT}:
                self._earth_shadow_add_currency('offworld_purchases_from_earth',tx.destination_location,tx.year,tx.amount)

    def record_earth_migration(self,year,count):
        count=int(count)
        if count<0: raise InvariantError('negative Earth migration shadow flow')
        ledger=self.state.earth_impact.migration_from_earth; year=int(year)
        ledger[year]=ledger.get(year,0)+count

    def earth_shadow_at(self,year):
        year=int(year); impact=self.state.earth_impact
        total=lambda mapping: sum((D(v) for (node,y),v in mapping.items() if y==year),D('0'))
        return {
            'capital_diverted_to_offworld':total(impact.capital_diverted_to_offworld),
            'capital_returned_to_earth':total(impact.capital_returned_to_earth),
            'offworld_purchases_from_earth':total(impact.offworld_purchases_from_earth),
            'earth_purchases_from_offworld':total(impact.earth_purchases_from_offworld),
            'qualifying_supplied_expenditure':total(impact.qualifying_supplied_expenditure),
            'terrestrial_fcf_delta':total(impact.terrestrial_fcf_delta),
            'migration_from_earth':int(impact.migration_from_earth.get(year,0)),
            'returning_population':int(impact.returning_population.get(year,0)),
        }

    def transfer(self,year,source,destination,amount,purpose,supplier_location=None,asset_location=None,parent_ids=()):
        amount=D(amount); s=self.state.accounts[source]; d=self.state.accounts[destination]
        if amount<0 or s.balance<amount: raise InvariantError(f'invalid transfer from {source}')
        s.balance-=amount; d.balance+=amount
        tx=Transaction(self._id('tx'),year,source,destination,amount,purpose,s.node_id,d.node_id,supplier_location,asset_location,tuple(parent_ids))
        self.state.transactions.append(tx); self._record_earth_shadow_transfer(tx); return tx
    def disburse(self,year,commitment_id,source_account,amount):
        c=self.state.commitments[commitment_id]; amount=D(amount)
        if amount>c.outstanding: raise InvariantError('disbursement exceeds commitment')
        p=self.state.projects[c.project_id]
        tx=self.transfer(year,source_account,p.cash_account_id,amount,TxPurpose.DISBURSE,parent_ids=(commitment_id,)); c.disbursed+=amount; return tx
    def spend_capex(self,year,project_id,supplier_account,amount,asset_id,asset_node,asset_class='PRODUCTIVE',financing_origin_nodes=None):
        if asset_id in self.state.assets: raise InvariantError('duplicate asset')
        p=self.state.projects[project_id]; supplier_node=self.state.accounts[supplier_account].node_id; amount=D(amount)
        tx=self.transfer(year,p.cash_account_id,supplier_account,amount,TxPurpose.CAPEX,supplier_node,asset_node,(project_id,))
        self.state.assets[asset_id]=Asset(asset_id,project_id,asset_node,AssetKind.WIP,amount)
        origins=tuple(sorted(financing_origin_nodes)) if financing_origin_nodes is not None else tuple(sorted({t.source_location for t in self.state.transactions if t.destination_account==p.cash_account_id and t.purpose in {TxPurpose.DISBURSE,TxPurpose.LOCAL_REINVESTMENT,TxPurpose.OTHER_INVESTMENT}}))
        fcf=FixedCapitalFormationEvent(self._id('fcf'),year,project_id,asset_id,tuple(sorted(p.owners)),origins,supplier_node,asset_node,amount,asset_class,(tx.id,))
        self.state.fcf_events.append(fcf)
        if self.state.nodes[supplier_node].kind==NodeKind.EARTH:
            key=(supplier_node,year); total=self.state.earth_impact.qualifying_supplied_expenditure.get(key,D('0'))+amount
            self.state.earth_impact.qualifying_supplied_expenditure[key]=total; self.state.earth_impact.terrestrial_fcf_delta[key]=-self.lambda_displacement*total
        return tx
    def capitalize(self,asset_id,capacity=D('0')):
        a=self.state.assets[asset_id]
        if a.kind!=AssetKind.WIP: raise InvariantError('only WIP can capitalize')
        a.kind=AssetKind.PRODUCTIVE; a.capacity=D(capacity)
    def realized_fcf(self,node_id,year): return sum((e.amount for e in self.state.fcf_events if e.asset_node==node_id and e.year==year),D('0'))
    def productive_capital(self,node_id): return sum((a.book_value for a in self.state.assets.values() if a.node_id==node_id and a.kind==AssetKind.PRODUCTIVE),D('0'))
    def assert_invariants(self):
        for c in self.state.commitments.values():
            if min(c.committed,c.disbursed,c.lapsed,c.outstanding)<0: raise InvariantError(f'commitment reconciliation {c.id}')
        for p in self.state.projects.values():
            if p.owners and sum(p.owners.values(),D('0'))!=D('1'): raise InvariantError(f'ownership {p.id}')
        # Multi-period WIP may receive multiple FCF additions under one construction id.
        # What is forbidden is cloning the same formation target across economic locations.
        locations={}
        for e in self.state.fcf_events:
            if e.asset_id in locations and locations[e.asset_id]!=e.asset_node: raise InvariantError('asset formation target cloned across locations')
            locations[e.asset_id]=e.asset_node
    def fingerprint(self):
        payload={'accounts':sorted((k,str(v.balance),v.node_id,v.kind.value) for k,v in self.state.accounts.items()),
                 'assets':sorted((k,str(v.book_value),str(v.capacity),v.node_id,v.kind.value) for k,v in self.state.assets.items()),
                 'tx':[(t.id,t.year,t.source_account,t.destination_account,str(t.amount),t.purpose.value,t.supplier_location,t.asset_location) for t in self.state.transactions],
                 'fcf':[(e.id,e.year,e.asset_id,e.supplier_node,e.asset_node,str(e.amount)) for e in self.state.fcf_events],
                 'impact':{
                    'qualifying_supplied_expenditure':sorted((k[0],k[1],str(v)) for k,v in self.state.earth_impact.qualifying_supplied_expenditure.items()),
                    'terrestrial_fcf_delta':sorted((k[0],k[1],str(v)) for k,v in self.state.earth_impact.terrestrial_fcf_delta.items()),
                    'capital_diverted_to_offworld':sorted((k[0],k[1],str(v)) for k,v in self.state.earth_impact.capital_diverted_to_offworld.items()),
                    'capital_returned_to_earth':sorted((k[0],k[1],str(v)) for k,v in self.state.earth_impact.capital_returned_to_earth.items()),
                    'offworld_purchases_from_earth':sorted((k[0],k[1],str(v)) for k,v in self.state.earth_impact.offworld_purchases_from_earth.items()),
                    'earth_purchases_from_offworld':sorted((k[0],k[1],str(v)) for k,v in self.state.earth_impact.earth_purchases_from_offworld.items()),
                    'migration_from_earth':sorted((int(k),int(v)) for k,v in self.state.earth_impact.migration_from_earth.items()),
                    'returning_population':sorted((int(k),int(v)) for k,v in self.state.earth_impact.returning_population.items()),
                 }}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()