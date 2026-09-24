# Reproducibility

Run from this project directory. Normal generation uses only local, hash-recorded
inputs.

```bash
python3 -B src/run_demography.py \
  --parameters parameters.json \
  --wpp-age /home/ubuntu/LOOM_Earth2026/raw/WPP2024_PopulationByAge5GroupSex_Percentage_Medium.csv.gz \
  --wpp-total /home/ubuntu/LOOM_Earth2026/raw/WPP2024_Demographic_Indicators_Medium.csv.gz \
  --v4-root /home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24 \
  --output-root /home/ubuntu/loom_earth_lean_biosynthetic_v0_20260924

python3 -B src/prepare_economic_boundary.py \
  --v4-root /home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24 \
  --output-dir /home/ubuntu/loom_earth_lean_biosynthetic_v0_20260924/v4_control_to_2100

python3 -B src/run_coupled_economy.py \
  --parameters parameters.json \
  --v4-root /home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24 \
  --checkpoint /home/ubuntu/loom_earth_lean_biosynthetic_v0_20260924/v4_control_to_2100/complete_checkpoints/earth_2100.checkpoint.zip \
  --demographic-root /home/ubuntu/loom_earth_lean_biosynthetic_v0_20260924 \
  --output-root /home/ubuntu/loom_earth_lean_biosynthetic_v0_20260924/coupled_successor

python3 -B src/validate_candidate.py \
  --demographic-root /home/ubuntu/loom_earth_lean_biosynthetic_v0_20260924 \
  --economic-root /home/ubuntu/loom_earth_lean_biosynthetic_v0_20260924/coupled_successor \
  --parameters parameters.json \
  --report /home/ubuntu/loom_earth_lean_biosynthetic_v0_20260924/independent_validation.json
```

The failed first boundary attempt, retained as
`v4_control_to_2100.failed-source-path`, documents that the governed v4 runner
rejects copied input paths. The successful reproduction uses the exact paths
declared in its manifest.
