"""Focused tests for the bounded, read-only replay position lookup."""
import unittest
from loom_world_authority.store import _RunEpoch, IntegrityFailure


class Cursor:
    def __init__(self, value):
        self.value = value

    def fetchone(self):
        return self.value


class Connection:
    def __init__(self, execution, ordinal=None, predecessor=None):
        self.responses = [execution]
        if execution is not None:
            self.responses.append((ordinal,))
            if ordinal is not None:
                self.responses.append(predecessor)
        self.queries = []

    def execute(self, statement, params):
        self.queries.append((statement, params))
        return Cursor(self.responses.pop(0))


class EpochPositionTests(unittest.TestCase):
    def session(self, connection, head=None):
        s = _RunEpoch.__new__(_RunEpoch)
        import threading
        s._RunEpoch__state = 'ACTIVE'
        s._RunEpoch__thread = threading.get_ident()
        s._RunEpoch__conn = connection
        s._RunEpoch__run = 'test-run'
        s._RunEpoch__head = head
        return s

    def lookup(self, s):
        return s.read_epoch_position('P1', input_snapshot_ref='input',
                                     code_contract='contract', code_tree_sha256='hash')

    def test_absent_execution(self):
        c = Connection(None)
        self.assertIsNone(self.lookup(self.session(c)))
        self.assertEqual(len(c.queries), 1)

    def test_existing_execution_new_epoch(self):
        c = Connection(('input', 'contract', 'hash'))
        self.assertEqual(self.lookup(self.session(c)), (False, None))
        self.assertEqual(len(c.queries), 2)

    def test_existing_epoch_with_predecessor(self):
        c = Connection(('input', 'contract', 'hash'), 17, ('E16', 'H16'))
        self.assertEqual(self.lookup(self.session(c)), (True, ('E16', 'H16')))
        self.assertEqual(len(c.queries), 3)

    def test_first_epoch_has_no_predecessor(self):
        c = Connection(('input', 'contract', 'hash'), 0, None)
        self.assertEqual(self.lookup(self.session(c)), (True, None))

    def test_wrong_execution_identity_rejected(self):
        c = Connection(('other', 'contract', 'hash'))
        s = self.session(c)
        with self.assertRaisesRegex(IntegrityFailure, 'REPLAY_IDENTITY_MISMATCH'):
            self.lookup(s)
        self.assertEqual(s._RunEpoch__state, 'FAILED')

    def test_head_without_execution_rejected(self):
        c = Connection(None)
        with self.assertRaisesRegex(IntegrityFailure, 'RUN_HEAD_WITHOUT_EXECUTION'):
            self.lookup(self.session(c, ('E', 'H', 1)))


if __name__ == '__main__':
    unittest.main()
