import unittest
from loom.runtime import resolve_runtime_roots
class CutoverImportSanity(unittest.TestCase):
 def test_import(self): self.assertTrue(callable(resolve_runtime_roots))
if __name__=='__main__':unittest.main()
