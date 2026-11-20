# Shuttle v3 step 3a: shape families in the bay
ALL bodies. ALL sponsors. 2026-2226. NON-CANON ROM screen. `shape_families.py` → `.json`, `shape_families_picture.py` → `shape_families.png`. Same aero tools as B4 (`../v2_lifting_body/aero_test.py`); entry at 58 t, glide at 43.5 t.

| Family | Volume m³ | Earth crossrange km | Glide L/D (fold / inflatable 14 m) |
|---|---:|---:|---|
| B4-S today | 82 | 1123 | 3.7 |
| F1 flying-boat lifting body | 81 | 502 | 5.0 / 6.9 |
| F2 lens | 53 | 945 | 3.5 (no wings) |
| F3 blended wing | 34 | 888 | 6.1 |
| F4 waverider | 13 | 858 | 4.4 |
| F5 D-section, flat belly | 120 | 266 | 4.4 / 6.1 |
| F6 D-section, shallow V | 124 | 248 | 4.4 / 6.0 |

Findings
1. The trade is volume against reach from orbit. Only the fullest sections (F5, F6) clear W2's 111 m³, and they lose about three quarters of the crossrange.
2. B4's sharp, flat-bellied angular body is still the best re-entry shape in the box. The families here are crude lofts; B4 is a drawn shape.
3. Glide L/D is held down by the torch base drag. A 14 m inflatable/telescoping wing gets ~6–7, not the ~12 Claude quoted in chat before running it.
4. Proposed W2 amendment (for kT): hull + deployable inflatable sponsons ≥ 111 m³; hull alone ≥ the volume displaced at the heaviest water landing (~74 m³). Sponsons also give the roll stability W6 needs with the side well flooded.
