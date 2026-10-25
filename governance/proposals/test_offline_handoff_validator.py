"""Fixture-only tests. Never contacts GitHub or Sydney."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

try:
    from governance.proposals.offline_handoff_validator import REQUIRED, validate
except ModuleNotFoundError:
    from offline_handoff_validator import REQUIRED, validate


class OfflineValidatorTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        files = []
        for path in REQUIRED:
            location = self.root / 'content' / path
            location.parent.mkdir(parents=True, exist_ok=True)
            data = path.encode('utf-8')
            location.write_bytes(data)
            files.append({'path': path, 'sha256': hashlib.sha256(data).hexdigest()})
        self.manifest = dict(schema_version=1, main_commit='c' * 40,
                             head_commit='a' * 40, base_commit='b' * 40,
                             approval_status='approved_governance_on_main',
                             capture_status='authenticated_verified',
                             scope_review_complete=True, files=files)
        self.save()

    def save(self):
        (self.root / 'manifest.json').write_text(json.dumps(self.manifest))

    def check(self, head='a' * 40, ancestor=True):
        return validate(self.root, head, ancestor)

    def test_complete_fixture_only(self):
        self.assertEqual(self.check(), [])

    def test_wrong_head(self):
        self.assertTrue(any('head mismatch' in e for e in self.check('d' * 40)))

    def test_unverified_ancestry(self):
        self.assertTrue(any('ancestry' in e for e in self.check(ancestor=False)))

    def test_modified_bytes(self):
        (self.root / 'content' / REQUIRED[0]).write_bytes(b'tampered')
        self.assertTrue(any('content mismatch' in e for e in self.check()))

    def test_missing_file(self):
        (self.root / 'content' / REQUIRED[0]).unlink()
        self.assertTrue(any('missing or symlink' in e for e in self.check()))

    def test_missing_inventory(self):
        self.manifest['files'].pop()
        self.save()
        self.assertTrue(any('missing required source' in e for e in self.check()))

    def test_unapproved_governance(self):
        self.manifest['approval_status'] = 'draft'
        self.save()
        self.assertTrue(any('approval absent' in e for e in self.check()))

    def test_unverified_provenance(self):
        self.manifest['capture_status'] = 'unknown'
        self.save()
        self.assertTrue(any('provenance' in e for e in self.check()))

    def test_scope_missing(self):
        self.manifest['scope_review_complete'] = False
        self.save()
        self.assertTrue(any('scope review' in e for e in self.check()))

    def test_bad_schema(self):
        self.manifest['schema_version'] = 2
        self.save()
        self.assertTrue(any('schema' in e for e in self.check()))

    def test_traversal(self):
        self.manifest['files'].append({'path': '../escape', 'sha256': '0' * 64})
        self.save()
        self.assertTrue(any('unsafe' in e for e in self.check()))

    def test_malformed_json(self):
        (self.root / 'manifest.json').write_text('{')
        self.assertTrue(any('malformed' in e for e in self.check()))


if __name__ == '__main__':
    unittest.main()
