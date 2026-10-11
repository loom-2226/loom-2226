"""Build 8 read-only deal view: evidence custody and work roles, not authority."""
from .deliverable_chain import OPERATORS

def deal_records(work, decisions, kernel):
    """Read only the receipts recorded during this economic trial."""
    return tuple({
        'project': 'screen:project:'+name,
        'sponsor': name,
        'financier': 'SCREEN_FINANCIER',
        'executors': tuple((category, OPERATORS[category][0]) for category in ('BUILD','LAND')),
        'decision': next((d for d in decisions if d[0]==name), None),
        'work': tuple(w for w in work if w.project==name),
        'evidence_routes': tuple(r for r in kernel.build8_knowledge
                                 if r[2] in (name,'SCREEN_FINANCIER','PUB')),
        'deal_terms': tuple(r for r in kernel.build8_knowledge
                            if r[1].startswith('deal:'+name+':')),
    } for name in ('Interlune','Axiom'))
