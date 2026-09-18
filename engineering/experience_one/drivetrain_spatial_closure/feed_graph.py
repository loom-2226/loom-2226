"""PR D abstract feed connectivity: no pressure, equipment sizing or geometry claims.

The protected reserve is an accounting boundary, NOT a located physical vessel.
External pack is optional and unqualified. Edges model permitted logical routes,
not certified pipes, valves, pressure drops, transient behavior or fault tolerance.
"""
from __future__ import annotations
from dataclasses import dataclass

TANKS = tuple(f'normal_tank_{i}' for i in range(1, 5))
EXTERNAL = ('external_tank_1', 'external_tank_2')
TORCH = 'torch_inlet'
RESERVE = 'protected_reserve_boundary'

@dataclass(frozen=True)
class FeedState:
    normal_open: tuple[bool, bool, bool, bool] = (True, True, True, True)
    external_attached: tuple[bool, bool] = (False, False)
    external_open: tuple[bool, bool] = (False, False)
    header_open: bool = True
    torch_enabled: bool = True
    high_metric_enabled: bool = False

    def __post_init__(self):
        if len(self.normal_open) != 4 or len(self.external_attached) != 2 or len(self.external_open) != 2:
            raise ValueError('four normal and two optional external identities required')
        if not all(type(v) is bool for v in (*self.normal_open, *self.external_attached, *self.external_open,
                                             self.header_open, self.torch_enabled, self.high_metric_enabled)):
            raise ValueError('state flags must be boolean')
        if self.torch_enabled and self.high_metric_enabled:
            raise ValueError('torch and high metric cannot operate simultaneously')
        if any(open_ and not attached for open_, attached in zip(self.external_open, self.external_attached)):
            raise ValueError('detached external tank cannot have open feed')


def edges(state: FeedState) -> frozenset[tuple[str, str]]:
    """Directed permission graph; isolation removes edges, never bypasses them."""
    links = set()
    for i, opened in enumerate(state.normal_open):
        if opened:
            links.add((TANKS[i], f'normal_isolator_{i + 1}'))
            links.add((f'normal_isolator_{i + 1}', 'normal_collector'))
    for i, (attached, opened) in enumerate(zip(state.external_attached, state.external_open)):
        if attached and opened:
            links.add((EXTERNAL[i], f'external_isolator_{i + 1}'))
            links.add((f'external_isolator_{i + 1}', 'external_manifold'))
    if state.header_open:
        links.add(('normal_collector', 'normal_header'))
        links.add(('external_manifold', 'normal_header'))
        links.add(('normal_header', 'conditioning_allocation'))
        if state.torch_enabled and not state.high_metric_enabled:
            links.add(('conditioning_allocation', TORCH))
    return frozenset(links)


def reachable(links: frozenset[tuple[str, str]], origin: str, destination: str) -> bool:
    seen = {origin}
    pending = [origin]
    while pending:
        node = pending.pop()
        if node == destination:
            return True
        for source, target in links:
            if source == node and target not in seen:
                seen.add(target)
                pending.append(target)
    return False


def verify_feed_state(state: FeedState) -> dict:
    links = edges(state)
    if any(RESERVE in link for link in links) or reachable(links, RESERVE, TORCH):
        raise ValueError('protected reserve has normal torch feed route')
    normal = tuple(reachable(links, tank, TORCH) for tank in TANKS)
    external = tuple(reachable(links, tank, TORCH) for tank in EXTERNAL)
    expected_normal = tuple(open_ and state.header_open and state.torch_enabled for open_ in state.normal_open)
    expected_external = tuple(attached and open_ and state.header_open and state.torch_enabled
                              for attached, open_ in zip(state.external_attached, state.external_open))
    if normal != expected_normal or external != expected_external:
        raise ValueError('unexpected feed reachability or isolation bypass')
    return {'status': 'PASS', 'normal_reachable': normal, 'external_reachable': external,
            'reserve_reachable': False, 'edge_count': len(links),
            'qualification': 'LOGICAL_CONNECTIVITY_ONLY_NOT_PHYSICAL_FEED_CERTIFICATION'}

if __name__ == '__main__':
    print(verify_feed_state(FeedState()))
