"""Opt-in defense draw. Parameters are authored, not military expenditure data."""
from dataclasses import dataclass
from decimal import Decimal as D
from offworld_kernel.kernel import InvariantError

CODE_VERSION = 'DEFENSE_DRAW_V1'

@dataclass(frozen=True)
class DefenseDials:
    overall_scale: D
    country_scale: D
    steepness: D
    cap: D

    def validate(self):
        values=(self.overall_scale,self.country_scale,self.steepness,self.cap)
        if any(not D(v).is_finite() or D(v)<0 for v in values) or self.steepness==0 or self.cap>1:
            raise InvariantError('invalid defense dials')
        return self

@dataclass(frozen=True)
class Crisis:
    name: str
    countries: tuple[str,...]
    start_year: int
    end_year: int
    intensity: D

    def validate(self):
        if not self.name or not self.countries or self.start_year>self.end_year or not D(0)<=self.intensity<=D(1):
            raise InvariantError('invalid authored crisis')
        return self

@dataclass(frozen=True)
class DefenseDrawRecord:
    year: int
    country: str
    pressure: D
    effective_pressure: D
    curve: D
    ceiling: D
    amount: D
    settings: DefenseDials
    crises: tuple[str,...]
    seed: str
    code_version: str
    transaction_id: str


def draw(kernel, year, country, investment_proxy, pressure, settings, units_per_model_currency, source_account, destination_account,
         *, crises=(), seed='DEFENSE-DRAW-TRIAL'):
    """Separate finite boundary draw. Disabled means do not call this function."""
    settings.validate();year=int(year);pressure=D(pressure)
    if not D(0)<=pressure<=D(1) or not seed:
        raise InvariantError('invalid defense pressure or seed')
    active=tuple(sorted(c.name for c in crises if country in c.countries and c.start_year<=year<=c.end_year))
    for c in crises:c.validate()
    if any(r.year==year and r.country==country for r in getattr(kernel,'defense_draw_records',())):
        raise InvariantError('duplicate country-year defense draw')
    from offworld_kernel.model import AccountKind, TxPurpose, Transaction
    src=kernel.state.accounts[source_account];dst=kernel.state.accounts[destination_account]
    if src.kind!=AccountKind.EARTH_BOUNDARY or src.node_id!='EARTH:'+country or dst.kind!=AccountKind.FUNDS or dst.node_id!=src.node_id:
        raise InvariantError('defense capital account scope')
    matches=[a for a in kernel.boundary_manifest.assertions if a.subject_id==country and a.concept=='investment'
             and a.world_context=='REAL' and a.valid_from==str(year)]
    if len(matches)!=1 or D(matches[0].value)!=D(investment_proxy):
        raise InvariantError('defense investment boundary mismatch')
    effective=min(D(1),pressure+sum((D(c.intensity) for c in crises if c.name in active),D(0)))
    curve=effective**settings.steepness
    # Ceiling is a fraction of admitted investment, NOT observed military expenditure.
    units=D(units_per_model_currency)
    if not units.is_finite() or units<=0:raise InvariantError('invalid defense unit normalization')
    ceiling=D(investment_proxy)/units*settings.cap
    amount=ceiling*min(D(1),settings.overall_scale*settings.country_scale*curve)
    src.balance-=amount;dst.balance+=amount
    kernel.boundary_net[source_account]=kernel.boundary_net.get(source_account,D(0))-amount
    tx=Transaction(kernel._id('tx'),year-2025,source_account,destination_account,amount,
                   TxPurpose.OTHER_INVESTMENT,src.node_id,dst.node_id,parent_ids=(CODE_VERSION,*active))
    kernel.state.transactions.append(tx)
    rec=DefenseDrawRecord(year,country,pressure,effective,curve,ceiling,amount,settings,active,seed,CODE_VERSION,tx.id)
    if not hasattr(kernel,'defense_draw_records'):kernel.defense_draw_records=[]
    kernel.defense_draw_records.append(rec)
    kernel.audit('DEFENSE_CAPITAL_DRAW',year,country=country,pressure=pressure,effective_pressure=effective,
                 curve=curve,ceiling=ceiling,amount=amount,overall_scale=settings.overall_scale,
                 country_scale=settings.country_scale,steepness=settings.steepness,cap=settings.cap,
                 crises=active,seed=seed,code_version=CODE_VERSION,transaction_id=tx.id)
    return rec
