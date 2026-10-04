from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Tuple
from .kernel import InvariantError
from .model import AccountKind, AssetKind, D, TxPurpose
from .mvp_state import ActionKind

@dataclass(frozen=True)
class SurplusDecompositionRecord:
    year:int
    project_id:str
    surplus:D
    reserve:D
    local_reinvest:D
    return_to_earth:D
    local_retention:D
    other_investment:D
    transaction_ids:Tuple[str,...]

    def validate(self):
        parts=self.reserve+self.local_reinvest+self.return_to_earth+self.local_retention+self.other_investment
        if min(self.surplus,self.reserve,self.local_reinvest,self.return_to_earth,self.local_retention,self.other_investment)<0:
            raise InvariantError('A6 negative surplus disposition')
        if parts!=self.surplus:
            raise InvariantError('A6 surplus decomposition')
        return self

@dataclass(frozen=True)
class AccountingPeriodSnapshot:
    period:int
    transaction_index:int
    event_index:int
    audit_index:int
    surplus_index:int
    account_balances:Tuple[Tuple[str,D],...]
    project_cash:Tuple[Tuple[str,D],...]
    wip_net:Tuple[Tuple[str,D],...]
    productive_total:D
    knowledge_total:D
    resource_remaining:Tuple[Tuple[str,D],...]

    @staticmethod
    def capture(kernel,period):
        return AccountingPeriodSnapshot(
            int(period),len(kernel.state.transactions),len(kernel.events),len(kernel.event_log),
            len(getattr(kernel,'surplus_decompositions',())),
            tuple(sorted((k,D(v.balance)) for k,v in kernel.state.accounts.items())),
            tuple(sorted((p.id,D(kernel.state.accounts[p.cash_account_id].balance)) for p in kernel.state.projects.values())),
            tuple(sorted((w.id,D(w.remaining_wip)) for w in kernel.wip.values())),
            sum((D(a.book_value) for a in kernel.state.assets.values() if a.kind==AssetKind.PRODUCTIVE),D('0')),
            sum((D(a.book_value) for a in kernel.state.assets.values() if a.kind==AssetKind.KNOWLEDGE),D('0')),
            tuple(sorted((rid,D(r.remaining)) for rid,r in kernel.resources.items())))

class AccountingIdentityAuditor:
    """Executable A1-A9 checks from the Offworld Financing Agent v2 identity set."""

    def __init__(self,kernel,snapshot:AccountingPeriodSnapshot):
        self.k=kernel; self.s=snapshot
        self.tx=self.k.state.transactions[self.s.transaction_index:]
        self.events=self.k.events[self.s.event_index:]
        self.audit=self.k.event_log[self.s.audit_index:]
        self.surplus=getattr(self.k,'surplus_decompositions',[])[self.s.surplus_index:]

    def _open_accounts(self): return dict(self.s.account_balances)
    def _open_project_cash(self): return dict(self.s.project_cash)
    def _open_wip(self): return dict(self.s.wip_net)
    def _open_resources(self): return dict(self.s.resource_remaining)

    def check_A1(self):
        for t in self.tx:
            if t.amount<0: raise InvariantError('A1 negative transaction amount')
            if t.source_account not in self.k.state.accounts or t.destination_account not in self.k.state.accounts:
                raise InvariantError('A1 transaction account missing')
            s=self.k.state.accounts[t.source_account]; d=self.k.state.accounts[t.destination_account]
            if t.source_location!=s.node_id or t.destination_location!=d.node_id:
                raise InvariantError('A1 transaction location mismatch')
        return True

    def check_A2(self):
        opening=self._open_accounts()
        ids=set(opening)|set(self.k.state.accounts)
        for aid in ids:
            if aid not in opening:
                opening[aid]=D('0')
            inflow=sum((t.amount for t in self.tx if t.destination_account==aid),D('0'))
            outflow=sum((t.amount for t in self.tx if t.source_account==aid),D('0'))
            close=self.k.state.accounts[aid].balance
            if close!=opening[aid]+inflow-outflow:
                raise InvariantError(f'A2 account rollforward {aid}')
        return True

    def check_A3(self):
        for c in self.k.state.commitments.values():
            if c.outstanding!=c.committed-c.disbursed-c.lapsed or c.outstanding<0:
                raise InvariantError(f'A3 commitment identity {c.id}')
        return True

    def check_A4(self):
        opening=self._open_project_cash()
        for p in self.k.state.projects.values():
            aid=p.cash_account_id
            start=opening.get(p.id,D('0'))
            inflow=sum((t.amount for t in self.tx if t.destination_account==aid),D('0'))
            outflow=sum((t.amount for t in self.tx if t.source_account==aid),D('0'))
            close=self.k.state.accounts[aid].balance
            if close!=start+inflow-outflow:
                raise InvariantError(f'A4 project cash rollforward {p.id}')
        return True

    def check_A5(self):
        opening_wip=self._open_wip()
        additions={}
        writeoffs={}
        capitalization=D('0'); depreciation=D('0'); amortization=D('0')
        for e in self.audit:
            if e['kind']=='WIP_ADDITION':
                additions[e['wip']]=additions.get(e['wip'],D('0'))+D(e['amount'])
            elif e['kind']=='WIP_WRITE_OFF':
                writeoffs[e['wip']]=writeoffs.get(e['wip'],D('0'))+D(e['amount'])
            elif e['kind']=='COMMISSION':
                capitalization+=D(e['value'])
            elif e['kind']=='DEPRECIATE':
                depreciation+=D(e['amount'])
            elif e['kind']=='KNOWLEDGE_AMORTIZE':
                amortization+=D(e['amount'])
        for wid,w in self.k.wip.items():
            opening=opening_wip.get(wid,D('0'))
            current=D(w.remaining_wip)
            commissioned=sum((D(e['value']) for e in self.audit if e['kind']=='COMMISSION' and e['wip']==wid),D('0'))
            written_off=writeoffs.get(wid,D('0'))
            if current!=opening+additions.get(wid,D('0'))-commissioned-written_off:
                raise InvariantError(f'A5 WIP rollforward {wid}')
        productive=sum((D(a.book_value) for a in self.k.state.assets.values() if a.kind==AssetKind.PRODUCTIVE),D('0'))
        if productive!=self.s.productive_total+capitalization-depreciation:
            raise InvariantError('A5 productive asset rollforward')
        knowledge=sum((D(a.book_value) for a in self.k.state.assets.values() if a.kind==AssetKind.KNOWLEDGE),D('0'))
        if knowledge!=self.s.knowledge_total-amortization:
            raise InvariantError('A5 knowledge rollforward')
        return True

    def check_A6(self):
        for r in self.surplus: r.validate()
        return True

    def check_A7(self):
        for p in self.k.state.projects.values():
            if not p.owners or sum(p.owners.values(),D('0'))!=D('1'):
                raise InvariantError(f'A7 project ownership {p.id}')
        return True

    def check_A8(self):
        for t in self.tx:
            if t.purpose!=TxPurpose.REVENUE: continue
            payer=self.k.state.accounts[t.source_account]
            if payer.kind==AccountKind.EARTH_BOUNDARY: continue
            if t.source_location!=t.destination_location:
                raise InvariantError(f'A8 revenue payer not boundary/local buyer {t.id}')
        return True

    def check_A9(self):
        opening=self._open_resources()
        extracted={}
        for e in self.events:
            if e.action==ActionKind.EXTRACT:
                rid=e.inputs[0]; q=D(e.inputs[1]); extracted[rid]=extracted.get(rid,D('0'))+q
        for rid,r in self.k.resources.items():
            start=opening.get(rid,D(r.in_situ))
            if D(r.remaining)!=start-extracted.get(rid,D('0')):
                raise InvariantError(f'A9 stock depletion {rid}')
        return True

    def check_all(self):
        checks={}
        for n in range(1,10):
            name=f'A{n}'; checks[name]=getattr(self,f'check_A{n}')()
        return checks
