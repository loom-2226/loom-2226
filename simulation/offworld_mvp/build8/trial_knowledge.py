"""Build 8 event-time knowledge receipts, scoped to one disposable trial."""


def record(kernel, fact, actor, route, source):
    if not hasattr(kernel, 'build8_knowledge'):
        kernel.build8_knowledge = []
    entry = (fact, actor, route, source)
    kernel.build8_knowledge.append(entry)
    kernel.audit('BUILD8_KNOWLEDGE', 2026, fact=fact, actor=actor, route=route, source=source)


def who_knows(kernel, fact):
    return tuple((actor, route, source) for key, actor, route, source
                 in kernel.build8_knowledge if key == fact)


def terms(kernel, project, parties, detail):
    fact = 'deal:' + project + ':' + detail
    for actor in parties:
        record(kernel, fact, actor, 'DEAL_PARTY', project)
    return fact
