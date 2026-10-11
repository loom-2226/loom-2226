"""Build 8 read-only deal view: evidence custody and work roles, not authority."""
from .sponsor_evidence_setup import sponsor_setup
from .deliverable_chain import OPERATORS

SPONSOR_MAP = {'A': 'Interlune', 'B': 'Axiom'}


def evidence_routes(private_signal='NEGATIVE', share_private=False):
    """Plain observation-recipient-route list from existing publication state.

    The evidence fixture is independent of the economic kernel. Its observation
    IDs are namespaced here to avoid pretending the two runs share authority.
    """
    kernel, public, _, private, _ = sponsor_setup(private_signal, share_private)
    rows=[]
    for obs in public:
        rows.append(('fixture:'+obs.id, 'PUB', 'OBSERVED', obs.question_ref))
        for name in ('A','B'):
            if obs.id in kernel.agents[name].information:
                rows.append(('fixture:'+obs.id, SPONSOR_MAP[name], 'PUBLISHED', obs.question_ref))
    rows.append(('fixture:'+private.id, 'Axiom', 'OBSERVED', private.question_ref+':'+private.signal))
    if private.id in kernel.agents['B'].information:
        rows.append(('fixture:'+private.id, 'Axiom', 'PRIVATE_RECEIPT', private.question_ref))
    if share_private and private.id in kernel.agents['A'].information:
        rows.append(('fixture:'+private.id, 'Interlune', 'SHARED', private.question_ref))
    # Financing snapshots use the derived posterior, not the private observation
    # itself. Distinguish disclosed evidence from a belief used in underwriting.
    for name in SPONSOR_MAP.values():
        rows.append(('fixture:posterior:VOLATILES', 'SCREEN_FINANCIER',
                     'DISCLOSED_BELIEF_BY_'+name, 'VOLATILES_PRESENT'))
    return tuple(rows)


def deal_records(work, decisions, private_signal='NEGATIVE', share_private=False):
    routes=evidence_routes(private_signal, share_private)
    return tuple({
        'project': 'screen:project:'+name,
        'sponsor': name,
        'financier': 'SCREEN_FINANCIER',
        'executors': tuple((category, OPERATORS[category][0]) for category in ('BUILD','LAND')),
        'decision': next((d for d in decisions if d[0]==name), None),
        'work': tuple(w for w in work if w.project==name),
        'evidence_routes': tuple(r for r in routes if r[1] in ('PUB', name, 'SCREEN_FINANCIER')),
    } for name in ('Interlune','Axiom'))
