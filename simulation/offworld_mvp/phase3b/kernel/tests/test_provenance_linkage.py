import os
import unittest
from pathlib import Path
from unittest.mock import patch

from offworld_kernel.kernel import InvariantError
from offworld_kernel.provenance import (
    git_object_source_tree_hash,
    source_tree_hash,
    verify_commit_code_linkage,
)

class ProvenanceLinkageTests(unittest.TestCase):
    def test_commit_code_linkage_uses_git_object_or_release_attestation(self):
        commit=os.environ.get('LOOM_GIT_COMMIT')
        if not commit:
            import subprocess
            commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        current=source_tree_hash()
        try:
            object_hash=git_object_source_tree_hash(commit)
        except InvariantError:
            self.assertEqual(os.environ.get('LOOM_EXPECTED_CODE_TREE_SHA256'),current)
            self.assertEqual(verify_commit_code_linkage(commit,current),'EXPORTED_CODE_HASH_ATTESTED')
        else:
            self.assertEqual(object_hash,current)
            self.assertEqual(verify_commit_code_linkage(commit,current),'GIT_OBJECT_VERIFIED')

    def test_exported_hash_attestation_rejects_mismatch(self):
        current=source_tree_hash()
        with patch('offworld_kernel.provenance.git_object_source_tree_hash',side_effect=InvariantError('no git')):
            with patch.dict(os.environ,{'LOOM_EXPECTED_CODE_TREE_SHA256':'0'*64},clear=False):
                with self.assertRaisesRegex(InvariantError,'does not match release attestation'):
                    verify_commit_code_linkage('1'*40,current)

    def test_exported_hash_attestation_accepts_exact_code_hash(self):
        current=source_tree_hash()
        with patch('offworld_kernel.provenance.git_object_source_tree_hash',side_effect=InvariantError('no git')):
            with patch.dict(os.environ,{'LOOM_EXPECTED_CODE_TREE_SHA256':current},clear=False):
                self.assertEqual(verify_commit_code_linkage('1'*40,current),'EXPORTED_CODE_HASH_ATTESTED')

if __name__=='__main__':
    unittest.main()
