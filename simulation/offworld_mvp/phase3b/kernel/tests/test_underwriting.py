import unittest
from decimal import Decimal as D
from offworld_kernel.underwriting import *
from offworld_kernel.kernel import InvariantError

class UnderwritingTests(unittest.TestCase):
    def test_validation_table_complete_and_explicit(self):
        t=mvp_validation_underwriting_table()
        self.assertEqual(t.epistemic_status,'PRE_CONTRACT_AUTHORED_SCENARIO')
        self.assertEqual(t.get('GENERIC_RESOURCE_PROJECT_MVP',UnderwritingInputKind.PRICE).value,D('20'))
        self.assertEqual(len(t.inputs),5)
        self.assertEqual(t.fingerprint(),mvp_validation_underwriting_table().fingerprint())

    def test_unknown_cannot_smuggle_number(self):
        with self.assertRaises(InvariantError):
            UnderwritingInput('x','A',UnderwritingInputKind.PRICE,D('0'),'U',
                UnderwritingInputStatus.UNKNOWN,'SRC').validate()

    def test_known_requires_value_and_units_source(self):
        with self.assertRaises(InvariantError):
            UnderwritingInput('x','A',UnderwritingInputKind.PRICE,None,'U',
                UnderwritingInputStatus.AUTHORED_SCENARIO,'SRC').validate()
        with self.assertRaises(InvariantError):
            UnderwritingInput('x','A',UnderwritingInputKind.PRICE,D('1'),'',
                UnderwritingInputStatus.AUTHORED_SCENARIO,'SRC').validate()

    def test_archetype_must_have_all_five_inputs(self):
        x=UnderwritingInput('p','A',UnderwritingInputKind.PRICE,D('1'),'U',
            UnderwritingInputStatus.AUTHORED_SCENARIO,'SRC')
        with self.assertRaisesRegex(InvariantError,'archetype incomplete'):
            UnderwritingTable('T','1','PRE_CONTRACT_AUTHORED_SCENARIO',(x,)).validate()

if __name__=='__main__': unittest.main()
