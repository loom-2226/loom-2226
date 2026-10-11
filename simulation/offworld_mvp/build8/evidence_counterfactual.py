"""Compare identical Sponsors under constrained versus immediate funding."""
from .screened_delivery import run_screened, SPONSORS


def compare_funding(private_signal='NEGATIVE', share_private=False):
    options={'private_signal':private_signal,'share_private':share_private}
    constrained,decisions,_,_=run_screened(**options)
    immediate,control_decisions,_,_=run_screened(immediate_funding=True,**options)
    output=[]
    for name in SPONSORS:
        funded=next(d[4] for d in decisions if d[0]==name)
        control=next(d[4] for d in control_decisions if d[0]==name)
        actual=next(r for r in constrained if r.project==name and r.category=='LAND')
        hypothetical=next(r for r in immediate if r.project==name and r.category=='LAND')
        output.append({'sponsor':name,'funded':funded,'immediate_funding':control,
                       'landed':actual.finish,'immediate_landing':hypothetical.finish,
                       'years_lost':actual.finish-hypothetical.finish,
                       'cash_difference':sum(r.revenue for r in immediate if r.project==name)
                                         -sum(r.revenue for r in constrained if r.project==name)})
    return tuple(output)
