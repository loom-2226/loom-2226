"""Correct leap-second load ordering without changing original builder."""
import hashlib
from pathlib import Path
import spiceypy as spice
from simulation.offworld_mvp.build8.three_arm_stage1.PR427_ASSIST_2035_BUILD_TEST_ONLY import main
LSK=Path('/home/ubuntu/loom_solar_assets/kernels/lsk/naif0012.tls')
assert hashlib.sha256(LSK.read_bytes()).hexdigest()=='678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b','LSK_HASH_MISMATCH'
spice.furnsh(str(LSK))
print('LSK_HASH_PASS_AND_LOADED',flush=True)
if __name__=='__main__':main()
