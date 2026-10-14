"""TEST_ONLY return destinations and explicitly authored project operators.

Reusable Build 8 mechanics; no default ownership classification or implicit grants.
"""
from offworld_kernel.model import AccountKind

SOURCE = 'resource_export_to_earth_buyer'
# (revenue source, economic owner type) -> (destination rule, appropriation delay)
DESTINATIONS = {
    (SOURCE, 'public_agency'): ('country_treasury', 3),
    (SOURCE, 'private_company'): ('company_funds', 0),
    (SOURCE, 'financier'): ('financier_claim_account', 0),
}


def agency_owner_type(agency, authored_rows):
    rows = [row for row in authored_rows if row[0] == agency]
    if len(rows) != 1 or not rows[0][1] or not rows[0][2]:
        raise ValueError('missing or ambiguous authored agency owner type: ' + agency)
    return rows[0][1]


def apply_operator_grants(kernel, authored_rows):
    """Only entry point for issuing project-scoped operator capabilities."""
    if len({(a, p) for a, p, _, _ in authored_rows}) != len(authored_rows):
        raise ValueError('duplicate operator grant')
    applied = []
    for agency, project, owner, reason in authored_rows:
        if (not reason or agency not in kernel.agents or
                project not in kernel.state.projects or
                owner not in kernel.state.projects[project].owners):
            raise ValueError('invalid authored operator grant: ' + str((agency, project, owner)))
        capability = 'OPERATE_PROJECT:' + project
        kernel.agents[agency].capabilities.add(capability)
        applied.append(dict(agency=agency, project=project, owner=owner,
                            capability=capability, reason=reason))
    return tuple(applied)


def resolve_destination(kernel, revenue_source, owner_type, owner_id, sponsor_id,
                        overrides=(), financing_claim=None):
    """Resolve destination from explicit economic type; never infer from AgentKind."""
    matching = [row for row in overrides
                if (row[0], row[1], row[2]) == (revenue_source, owner_type, owner_id)]
    if len(matching) > 1:
        raise ValueError('ambiguous owner override')
    rule = (matching[0][3], matching[0][4]) if matching else DESTINATIONS.get(
        (revenue_source, owner_type))
    if rule is None:
        raise ValueError('missing return destination rule: ' + str((revenue_source, owner_type)))
    destination_kind, delay = rule
    if sponsor_id not in kernel.agents:
        raise ValueError('unregistered sponsor')
    country_node = kernel.agents[sponsor_id].node_id
    if not country_node.startswith('EARTH:'):
        raise ValueError('sponsor country unavailable')
    country = country_node.removeprefix('EARTH:')
    if destination_kind == 'country_treasury':
        if owner_id != 'STATE:' + country:
            raise ValueError('treasury owner/country mismatch')
        account = 'treasury:' + country
    elif destination_kind == 'company_funds':
        account = kernel._distribution_owner_account(owner_id)
    elif destination_kind == 'financier_claim_account':
        if financing_claim is None or financing_claim.financier_id != owner_id:
            raise ValueError('financier destination requires matching validated claim')
        account = financing_claim.destination_account_id
    else:
        raise ValueError('unknown authored return destination kind')
    if account not in kernel.state.accounts:
        raise ValueError('return destination account missing: ' + account)
    target = kernel.state.accounts[account]
    if target.owner_id != owner_id:
        raise ValueError('return destination ownership mismatch')
    if destination_kind == 'country_treasury':
        matches = [a for a in kernel.state.accounts.values()
                   if a.owner_id == owner_id and a.kind == AccountKind.FUNDS]
        if (len(matches) != 1 or target.kind != AccountKind.FUNDS
                or target.node_id != country_node):
            raise ValueError('treasury must own exactly one Earth FUNDS account')
    return dict(account=account, owner_id=owner_id, owner_type=owner_type,
                country=country, destination_kind=destination_kind, delay_years=delay)
