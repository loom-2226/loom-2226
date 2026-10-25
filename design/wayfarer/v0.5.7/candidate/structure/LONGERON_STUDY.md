# Wayfarer longerons: four or five, sized, Osteon at the joints

ALL bodies. ALL sponsors. 2026-2226.

**NON-GOVERNING STUDY, 2026-10-25.** Baseline: v0.5.6 (geometry `14bb3c2c...`). **Adopted into the v0.5.7 candidate** with conventional joints; see `CHANGES_v0.5.7.md`. Integration found that the longeron lines lie under the stowed strakes, so node mounts go on frames in the clear arcs and the service bands are not built. It also found that the old planks screened the berths, so a 0.6 t service shield band was added. Numbers come from `structure/longeron_study.py` (results in `longeron_study_results.json`, figure `longeron_study.png`). Closed-form, using the same load model as G5.

## 1. Four or five: four

**Recommendation:** four CFRP tubes in an X, at 43.4° either side of the vertical, above and below. The upper pair stay exactly where today's slot sills are. The lower pair mirror them, set into the tank's lower cells. The three planks go.

| | Five (v0.5.6 layout, sized) | Four tubes (sized) |
|---|---|---|
| Canon ("4 axial longerons") | Declared departure | **Matches** |
| Span mass | 15.1 t | **10.6 t** |
| Why | The 18 cm gap between the tank and the skin forces wide, thin planks. These buckle before they reach their stress limit, so they end up oversized. | Tubes are stress-governed; buckling margin 21x |
| Joints | 10 end fittings, 25 node mounts and hatches | 8 end fittings, 20 node mounts and hatches |
| Tank volume | 322.6 m³ | 321.1 m³ (need 315) |
| Strake roots | **Sills overlap them by 2.8 cm** | Clear by 2.2 cm, plus root housings |
| Node directions | 3 on node azimuths, 2 off by 1.6° | All 4 off by 1.6° (about 10 cm, bridged by the mount) |

**v0.5.6 finding, for Sol:** the 0.5 m sills reach 2.8 cm into the stowed strake roots at 40° and 140°. It's small, but it's a real overlap in the current package. Either 0.4 m tubes or a strake root 5 cm further out would clear it.

## 2. Sizing pass

**Load:** the same as G5. 1,005 t ahead of the thrust cone (state S2) at 5 g x 1.5, which gives 73.9 MN. All of it is put on the longerons. That's conservative, because the tank walls also carry the water.

**Design stress:** 250 MPa. This is the 400 MPa floor with a 0.62 knockdown for impact damage, joints and environment. It's a stated assumption.

**Four 0.40 m tubes with 72 mm walls:**

| Check | Value | Limit |
|---|---|---|
| Stress at 5 g x 1.5 | 250 MPa | 250 |
| Buckling between 2 m frames (Euler and local shell) | 21x | 1.5 |
| One longeron lost, 1 g, including the bending from the off-centre load | 67 MPa | 250 |
| First bending mode (longerons only) | 4.5 Hz | 1.0 |
| Twist: closed tank cell wall, 0.5 g side load at a 0.5 m offset (3.7 MN·m) | 10 MPa shear | 60 |
| Twist: the 0.8 m of open slot aft of the tank, carried by the tubes in bending | 19 MPa | 250 |

**Twist is not a driver.** The tank's closed C-cell carries it, as G5's torsion-mode check already assumed. The only open stretch is the 0.8 m between the tank end (x 31.5) and the slot end (x 32.3), and the tubes bridge that easily.

**v0.5.6 longerons:** 36.9 t at 65 MPa. Nothing checked made them that size. They also had **no end fittings or node mounts** in the ledger, so the sized figures below add them.

## 3. Osteon only at the joints

The straight spans stay plain CFRP tubes. A member carrying steady end-to-end load is already ideal as a tube, so optimising its shape gains nothing.

Osteon structure (topology-optimised, graded, Builder-derived OST-22) goes only where load changes direction:

| Item | Count | Conventional |
|---|---|---|
| End fittings: habitat ring at x 14 and thrust cone at x 34.3 (titanium, 18.5 MN each at ultimate) | 8 | 1.70 t |
| Node mounts on the ring frames: 5 of the 13 node rings fall on x 14-34.3 | 20 | 0.80 t |
| Flush node access hatches | 20 | 0.30 t |
| Bay-slot corners | 4 | 0.48 t |
| Strake-root housings | 4 | 0.20 t |
| **Total** | | **3.47 t** |

With Osteon structure (30-50% lighter on everything except the fixed bolt-and-shim allowance), the total is **2.1-2.7 t, central 2.4 t**.

### Where the node mounts go (revised after review)

The sized tubes run **inside the remass tank**, about 0.7 m under the skin, just as today's sills do. A node mounted directly on a longeron would therefore sit in water, with no access and nowhere to run its 20 K cryogenic line.

- **Mount:** each node goes on the ring frame nearest its station, in the dry 18 cm gap between the tank and the skin. That frame ties into the longeron, so load and alignment still go to the longeron.
- **Station offset:** frames are every 2 m, so the five stations (x 14.35, 18.45, 22.55, 26.65, 30.75) sit 0.35-0.75 m from a frame. Either the node rings shift onto the frames, or short intermediate frames are added. **Sol and kT to choose.** Node placement in PR #184 is provisional.
- **Access:** from outside, through a flush hatch per node.

### What shows on the outside

- **Flush service bands:** one strip of access panels along each of the four longeron lines, x 14-34.3, with node hatches at the stations. This is the honest outside version of a "spine". The structure stays inside, and the bands give the lengthwise lines that break up the sandworm look. The raised spines and knuckles in the options collage are styling, not engineering.
- **Strake-root housings:** a shallow fairing at each stowed strake root. It fixes the 2.8 cm sill clash found above and tidies the look.
- **Not adopted:** a faceted hull. Nothing structural, armour-related or dust-related calls for it.

## Result

| | Mass | Back to the reserve |
|---|---|---|
| v0.5.6 | 36.9 t | — |
| Four tubes, conventional joints | 14.0 t | 22.9 t |
| **Four tubes, Osteon joints** | **12.9 t** | **23.9 t** (23.7-24.2) |

Almost all of the saving comes from sizing. Osteon adds about 1 t. It earns its place through stiffness and alignment at the node mounts, which is where the Loom hardware needs it, not through mass.

## Not done, and what could change it

- **Node-mount requirements:** stiffness, alignment tolerance and temperature. Canon is silent, and this could govern the longerons. **Sol to supply.**
- **Integration into a v0.5.7 build.** Removing about 24 t at x 14-34 moves trim. The reserve rises from 42.6 t to about 67 t; because the reserve is spread over every part, that also raises radiation screening. Every gate needs rerunning, and the canon amendment drops the five-longeron departure.
- **Node mounts:** they now sit on the frames, not the longerons (see above).
- **Habitat (x 0-14):** the forward three node rings are mounted by the habitat shell, not the longerons. The spine look over the habitat needs its own justification, for example external armour stiffeners.
- **Fidelity:** fittings are rough closed-form estimates. A finite-element model of the joints is the next step if the direction is adopted.
