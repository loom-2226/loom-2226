"""Phase 6 certification/reporting institution boundary.

NON_CANON / UNPROMOTED. Seed identity, confidence, verification, membership,
or reporting-code existence never grants authority over a space-resource claim.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class CertificationInstitutionV03:
    actor_id: str
    name: str
    confidence: str
    verified_by_search: bool
    status_2026: str | None
    verify_note: str | None
    authority_class: str = "NON_CANON_2026_INSTITUTION_CANDIDATE"

@dataclass(frozen=True)
class CertificationAuthorityV03:
    actor_id: str
    claim_domain: str
    jurisdiction: str
    authority_status: str
    basis: str
    authority_class: str = "AUTHORED_CERTIFICATION_AUTHORITY_ASSERTION"

def certification_institutions_from_seed(seed):
    return tuple(
        CertificationInstitutionV03(
            x["id"], x["name"], x.get("conf", "UNKNOWN"),
            bool(x.get("verified_by_search", False)), x.get("status_2026"),
            x.get("verify")
        )
        for x in seed["actors"] if x.get("category") == "CERTIFICATION"
    )

def authority_for(*, institution, claim_domain, jurisdiction, explicit_authority, basis):
    return CertificationAuthorityV03(
        institution.actor_id, claim_domain, jurisdiction,
        "AUTHORIZED" if explicit_authority else "UNKNOWN", basis
    )

def may_qualify(authority):
    return authority.authority_status == "AUTHORIZED"
