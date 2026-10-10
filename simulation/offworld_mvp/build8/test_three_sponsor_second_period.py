"""Two periods, one kernel: carry forward private information, cash, and projects."""
import unittest
from decimal import Decimal as D
from .test_three_sponsor_consequences import episode

class SecondPeriod(unittest.TestCase):
    def test_carry_forward_without_reset(self):
        for positive in (False,True):
            (first,second),transactions=episode(positive,periods=2)
            self.assertEqual(((first,second),transactions),episode(positive,periods=2))
            self.assertEqual(first['A'],first['C'])
            self.assertEqual(second['A'],second['C'])
            for sponsor in ('A','B','C'):
                self.assertEqual(D(second[sponsor][3]),D(first[sponsor][3])-(D('.25') if second[sponsor][0]=='INITIATE_PROJECT' else D(0)))
                self.assertEqual(D(second[sponsor][2]),D(first[sponsor][2])+(D('.25') if second[sponsor][0]=='INITIATE_PROJECT' else D(0)))
                self.assertEqual(D(second[sponsor][2])+D(second[sponsor][3]),D(1))
            self.assertEqual(second['B'][0],'INITIATE_PROJECT' if positive else 'DECLINE')
            self.assertEqual(sum(D(t[2]) for t in transactions if t[3]=='OTHER_INVESTMENT'),D('1.50') if positive else D('1.00'))
            print('SECOND_PERIOD',positive,first,second)
