"""Build 8 event-time knowledge receipts, scoped to one disposable trial."""


def record(kernel, year, fact, actor, route, source):
    if not hasattr(kernel, 'build8_knowledge'):
        kernel.build8_knowledge = []
    entry = (int(year), fact, actor, route, source)
    kernel.build8_knowledge.append(entry)
    kernel.audit('BUILD8_KNOWLEDGE', int(year), fact=fact, actor=actor, route=route, source=source)


def who_knows(kernel, fact):
    return tuple((year, actor, route, source) for year, key, actor, route, source
                 in kernel.build8_knowledge if key == fact)


def terms(kernel, year, project, parties, detail):
    fact = 'deal:' + project + ':' + detail
    for actor in parties:
        record(kernel, year, fact, actor, 'DEAL_PARTY', project)
    return fact


def outcome(kernel, year, project, status, parties, detail=''):
    """Record outcome visibility only for actors directly party to it."""
    fact = 'outcome:' + project + ':' + status + (':' + detail if detail else '')
    for actor in parties:
        record(kernel, year, fact, actor, 'DEAL_PARTY', project)
    return fact
