import unittest
from decimal import Decimal as D
from offworld_kernel.underwriting import *
from offworld_kernel.kernel import InvariantError

class UnderwritingTests(unittest.TestCase):
    def test_validation_table_complete_explicit_and_time_indexed(self):
        t=mvp_validation_underwriting_table()
        self.assertEqual(t.epistemic_status,'PRE_CONTRACT_AUTHORED_SCENARIO')
        price=t.get('GENERIC_RESOURCE_PROJECT_MVP',UnderwritingInputKind.PRICE)
        self.assertEqual(price.value,D('20'))
        self.assertEqual(price.unit,'MODEL_CURRENCY_PER_RESOURCE_UNIT')
        self.assertEqual(price.basis_year,1)
        self.assertEqual((price.valid_from,price.valid_to),(1,1))
        self.assertEqual(len(t.inputs),5)
        self.assertEqual(t.fingerprint(),mvp_validation_underwriting_table().fingerprint())

    def test_unknown_cannot_smuggle_number(self):
        with self.assertRaises(InvariantError):
            UnderwritingInput('x','A',UnderwritingInputKind.PRICE,D('0'),'U',
                UnderwritingInputStatus.UNKNOWN,'SRC',1,valid_from=1,valid_to=1).validate()

    def test_known_requires_value_units_source_and_year_scope(self):
        with self.assertRaises(InvariantError):
            UnderwritingInput('x','A',UnderwritingInputKind.PRICE,None,'U',
                UnderwritingInputStatus.AUTHORED_SCENARIO,'SRC',1,valid_from=1,valid_to=1).validate()
        with self.assertRaises(InvariantError):
            UnderwritingInput('x','A',UnderwritingInputKind.PRICE,D('1'),'',
                UnderwritingInputStatus.AUTHORED_SCENARIO,'SRC',1,valid_from=1,valid_to=1).validate()
        with self.assertRaisesRegex(InvariantError,'validity years missing'):
            UnderwritingInput('x','A',UnderwritingInputKind.PRICE,D('1'),'U',
                UnderwritingInputStatus.AUTHORED_SCENARIO,'SRC',1).validate()
        with self.assertRaisesRegex(InvariantError,'basis year outside'):
            UnderwritingInput('x','A',UnderwritingInputKind.PRICE,D('1'),'U',
                UnderwritingInputStatus.AUTHORED_SCENARIO,'SRC',2,valid_from=1,valid_to=1).validate()

    def test_archetype_must_have_all_five_inputs(self):
        x=UnderwritingInput('p','A',UnderwritingInputKind.PRICE,D('1'),'U',
            UnderwritingInputStatus.AUTHORED_SCENARIO,'SRC',1,valid_from=1,valid_to=1)
        with self.assertRaisesRegex(InvariantError,'archetype incomplete'):
            UnderwritingTable('T','1','PRE_CONTRACT_AUTHORED_SCENARIO',(x,)).validate()

    def test_table_can_be_admitted_as_year_scoped_snapshot_facts(self):
        t=mvp_validation_underwriting_table()
        facts=underwriting_snapshot_facts(t,'GENERIC_RESOURCE_PROJECT_MVP',1)
        self.assertEqual(len(facts),5)
        by_key={f.key:f for f in facts}
        self.assertEqual(by_key['underwriting.PRICE'].value,'20')
        self.assertIn('MODEL_CURRENCY_PER_RESOURCE_UNIT',by_key['underwriting.PRICE'].source_ref)
        self.assertIn('basis_year=1',by_key['underwriting.PRICE'].source_ref)
        self.assertIn('valid=1-1',by_key['underwriting.PRICE'].source_ref)
        self.assertTrue(all(f.state.value=='KNOWN' for f in facts))

    def test_table_rejects_decision_outside_valid_year(self):
        with self.assertRaisesRegex(InvariantError,'not valid for decision year'):
            underwriting_snapshot_facts(mvp_validation_underwriting_table(),'GENERIC_RESOURCE_PROJECT_MVP',2)

if __name__=='__main__': unittest.main()
