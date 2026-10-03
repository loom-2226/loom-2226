import unittest
from types import SimpleNamespace
from .authority_resolution_v0_3 import *
class T(unittest.TestCase):
 def test_estimated_capacity_requires_explicit_allocation(self):
  x=SimpleNamespace(actor_id="CAP_X",financial_capacity_estimate=100.0)
  a=allocate_financing(capital_identity=x,proposition_id="P",amount=40.0)
  self.assertEqual(a.status,AuthorityStatus.KNOWN);self.assertEqual(a.value,40.0)
  self.assertEqual(a.path,ResolutionPath.COUNTERPARTY_TRANSACTION)
 def test_allocation_cannot_exceed_capacity(self):
  x=SimpleNamespace(actor_id="CAP_X",financial_capacity_estimate=100.0)
  a=allocate_financing(capital_identity=x,proposition_id="P",amount=40.0,already_allocated=70.0)
  self.assertEqual(a.status,AuthorityStatus.UNKNOWN)
 def test_interest_does_not_resolve_capability(self):
  a=provider_from_typed_capability(provider_actor_id="SUP",capability_status="UNKNOWN",proposition_id="P")
  self.assertEqual(a.status,AuthorityStatus.UNKNOWN)
 def test_typed_transport_resolves_only_feasible_or_infeasible(self):
  self.assertEqual(transport_from_accessibility(assessment_status="FEASIBLE",provider_actor_id="C",proposition_id="P").satisfied,True)
  self.assertEqual(transport_from_accessibility(assessment_status="UNKNOWN",provider_actor_id="C",proposition_id="P").status,AuthorityStatus.UNKNOWN)
if __name__=="__main__":unittest.main()
