# Approved recovered Phase4E kernels: three registered-path exclusions

TEST_ONLY / NON-CANON. These are approved recovered Phase4E sources already used for earlier Stage 1 tables. Their files exist and their SHA-256 values exactly match the previously committed `VM_KERNEL_POSITION_MANIFEST.txt`. Do not conflate a missing original registry path with a missing kernel.

| Body | Approved recovered kernel | SHA-256 | Exists | Source label |
|---|---|---|---|---|
| APOPHIS | `/home/ubuntu/LOOM-output/PHASE4E_RECOVERY_20261020/apophis_2026_2251.bsp` | `adadefa7fc6722343305e3ccefd998af843dba7d1e7240a4bcfd08a96eaeb307` | YES | `recovered_phase4e` |
| ARROKOTH | `/home/ubuntu/LOOM-output/PHASE4E_RECOVERY_20261020/arrokoth_2026_2251.bsp` | `9c0146d456a9762fa16345e1937da523b333718c3f87698060984273f7d1d2ea` | YES | `recovered_phase4e` |
| ATLAS3I | `/home/ubuntu/LOOM-output/PHASE4E_RECOVERY_20261020/atlas3i_2026_2251.bsp` | `fca6353e3e874c79e105d6a039c5a027718da1691cc911f40875cfdbbd5f398f` | YES | `recovered_phase4e` |

Earlier **“qualified to 2031”** referred to the supported date range of the Stage 1 position tables and their sampled checks, not a physical guarantee that the underlying 2026–2251 SPK files become invalid in 2032. Extending the tables beyond 2031 requires checking the SPK's actual object/time coverage and producing new sampled comparisons over the extended interval. An independent SPICE oracle check can establish that sampled table states agree with the specified kernel under the stated frame, observer, and time conversion. It **cannot** establish that the kernel represents the true physical trajectory beyond 2031, validate its original orbit determination, or eliminate interpolation/model uncertainty between sampled dates. Scalar and vector calls to the same SPICE kernel are not independent scientific evidence; they are an implementation cross-check.

Recovered files are not substituted into the registered asset tree. Each new table must identify the recovered path and `recovered_phase4e` explicitly. No such recovered-source table has been qualified yet in this checkpoint.
