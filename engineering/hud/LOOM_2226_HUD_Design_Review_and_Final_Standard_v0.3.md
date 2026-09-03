**LOOM 2226**

**HUD Design Review, Response to External Critique,  
and Final Tactical Display Standard**

*Working Technical Standard v0.3 • 14 August 2026*

Purpose: document what the external critiques got right, where they
overreached, what was learned from the HUD design challenge, and the
resulting locked LOOM 2226 solution.

# 1. Executive Outcome

**The external critiques were useful.** They did not invalidate the
underlying LOOM HUD architecture; they exposed production-hardening
problems: mobile width, Unicode/emoji reliability, provenance honesty,
presentation-layer overload, and the need to separate spatial
comprehension from threat prioritization.

**The resulting design is not a single wunder-HUD.** It is an instrument
family sharing one deterministic simulation state. The default tactical
picture remains true 3D geometry; compact and triage views are optional
transformations of that same state.

NAV / SYSTEM  
where known bodies should be  
  
SENSOR / WIDE  
what is beginning to be perceived  
  
TACTICAL / TRACK  
where resolved contacts are in 3D  
  
TACTICAL / COMPACT  
optional compressed spatial summary  
  
TACTICAL / TRIAGE  
what deserves attention first

**Locked default tactical package:** MAIN + TOP + RANGE + CONTACTS. SIDE
is conditional/on request. COMPACT is optional. TRIAGE appears when
useful or when requested.

# 2. What the External Critiques Got Right

| **Critique**                     | **Judgement**         | **v0.3 Response**                                                                                                                                                   |
|----------------------------------|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Purpose ambiguity                | Correct.              | The document mixed an engineering specification with a player-facing operating interface. v0.3 explicitly separates simulation standard from presentation profiles. |
| Emoji vs. monospace              | Correct in substance. | Emoji may be a cosmetic skin only. Canonical HUD grammar is monospace text and must work without color or emoji.                                                    |
| Provenance honesty               | Strongly correct.     | A label describes what the runtime actually used. SPICE may be shown only if SPICE was actually evaluated.                                                          |
| Phone width                      | Correct.              | Mandatory tactical displays are designed around an approximately 38-column budget and may not rely on wrapping or horizontal scrolling.                             |
| Cognitive-load tiering           | Correct.              | Standard Play and NAV-GRADE are different presentation profiles over the same simulation state.                                                                     |
| Truth vs. observation separation | Core architecture.    | This is promoted as a governing LOOM rule, not merely a HUD concern.                                                                                                |
| Track quality earned over time   | Core architecture.    | Detection -\> Coarse -\> Firm -\> Tactical -\> Fire-Control remains canonical.                                                                                      |

# 3. Where the Critiques Overreached or Needed Correction

- Emoji did not move the sacred plotted cell in the prototype; that
  failure had already been anticipated by keeping the plotted marker
  independent. The real remaining problem was wrapping and
  cross-platform width, so emoji were still demoted.

- Ephemeris provenance and spacecraft track quality must not be merged.
  SPICE/Horizons/PDS describe how a natural-body navigation state was
  generated; DET/COARSE/FIRM/TACTICAL/FC describe the quality of a
  sensor-derived contact track.

- A 'SPICE-verified enemy spacecraft' is conceptually wrong. SPICE can
  tell the system where Titan should be; sensors tell the player where
  K1 appears to be.

- A threat-priority display is valuable, but it cannot replace spatial
  geometry. It answers 'what matters?' rather than 'where is it?'

- Numeric/ledger-only approaches are fast but discard spatial gestalt.
  They are therefore modes, not the primary 3D tactical interface.

# 4. What We Learned From the HUD-Off

Six alternative architectures were pressure-tested. None displaced the
primary TRACK display, but several contributed useful ideas.

| **Idea**                  | **Disposition**                                                                                                                          |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| Dual orthographic slices  | Validated the core insight that multiple projections are the cleanest text-only way to preserve genuine 3D geometry.                     |
| Bearing/mark ladder       | Useful as a compressed orientation summary; retained only as optional COMPACT mode.                                                      |
| Triage stack              | Excellent human-factors tool for prioritization; retained as TACTICAL / TRIAGE.                                                          |
| Ledger-only tactical view | Rejected as primary because precision without spatial gestalt is insufficient for maneuver.                                              |
| Octant grid               | Useful vocabulary, but a 2D grid cannot honestly encode all three signed spatial axes without the accompanying list doing the real work. |

# 5. Final Locked Tactical Display Standard

## 5.1 Default Instrument Family

MAIN  
port/starboard + dorsal/ventral  
  
TOP  
port/starboard + forward/aft  
  
RANGE  
distance/depth only  
  
CONTACTS  
exact kinematics + track quality  
  
SIDE  
conditional/on request  
  
COMPACT  
optional compressed summary  
  
TRIAGE  
priority when needed


### 5.1.1 FLIGHT / OWN minimum state

The tactical package may remain MAIN + TOP + RANGE + CONTACTS, but the ownship block must expose the engineering variables needed to interpret those views.

At minimum when material:

```text
FLIGHT / OWN
MASS      current wet
PACC      propulsive accel
NACC      net accel
ATT       current attitude
REMASS    t / %
THERM     state + trend
SIG       state
EPH       source
NAV REF   frame/reference
```

`ACC` alone is not acceptable when local gravity, rotation, or other field effects make zero thrust different from zero net acceleration.

When chronology materially diverges:

```text
SHIP MET      <mission proper/elapsed time>
EXT EPOCH     <best external epoch + standard>
CAUSAL OFFSET <difference + uncertainty/status>
```

These are separate clocks, not alternate labels for one timestamp.

## 5.2 Position, Attitude, Radial Motion, Hazard and Staleness

**Canonical contact grammar:** the first glyph is the plotted position.
If attitude is resolved, the attitude arrow itself occupies the sacred
plotted cell.

\*K1C resolved position  
attitude unresolved  
closing  
  
\*K2C! resolved position  
closing  
predicted hazard  
  
↖K3M resolved position  
resolved attitude  
nose projects ↖  
range matched  
  
\*K4O~ resolved position  
opening  
stale/coasting track

Locked suffix/state grammar:

| **Token** | **Meaning**                                     | **Important limitation**                       |
|-----------|-------------------------------------------------|------------------------------------------------|
| \*        | Resolved plotted position; attitude unresolved  | Never substitute a label for the plotted cell. |
| ATT ARROW | Resolved nose attitude projected into this view | ATTITUDE, never velocity.                      |
| C         | Closing: radial range decreasing                | Not total relative velocity.                   |
| O         | Opening: radial range increasing                | Not necessarily safe.                          |
| M         | Matched / near-zero radial range rate           | Transverse motion may still be large.          |
| ?         | Required state unresolved                       | Do not infer missing precision.                |
| !         | Predicted hazard geometry                       | Not hostility/allegiance.                      |
| ~         | Stale/coasting/extrapolated track               | Selected telemetry should expose age.          |

## 5.3 Uncertainty Is Geometry

**A point glyph is a privilege earned by sufficient positional track
quality.** Unresolved detections are represented as areas, bands or
intervals, never as falsely precise points.

\[ K7? \]  
.......  
  
BRG 286 +/-8 deg  
MRK unresolved  
RNG unresolved  
TRK DETECTION

## 5.4 Track Quality

D DETECTION  
C COARSE TRACK  
F FIRM TRACK  
T TACTICAL TRACK  
FC FIRE-CONTROL QUALITY

Track quality is not a distance band. It emerges from emissions,
aperture, observation time, geometry, baseline, occlusion, EW, target
aspect and relative motion.

## 5.5 Default 3D Reading

TRACK / MAIN  
  
DOR  
^  
\*K4O \| \*K1C  
\|  
PT \<----------O----------\> SB  
\|  
↖K3M \| \*K2C  
v  
VEN

MAIN answers: which side of me, and above or below?

TRACK / TOP  
  
FOR  
^  
\*K4O \| \*K1C  
\|  
PT \<----------O----------\> SB  
\|  
←K3M \| \*K2C  
v  
AFT

TOP answers: which side of me, and ahead or behind? The different K3
arrow is the same 3D attitude projected into a different plane.

RANGE  
  
\<100k \| K1C  
100-500\| K2C  
500k-1M\| K3M  
\>1M \| K4O  
\|OWN

RANGE answers distance only. Direction and distance are intentionally
not conflated.

ID RNG(km) RR TRK  
K1 92k -8.4 F  
K2 310k -27.8 T  
K3 640k +0.2 FC  
K4 1400k +6.7 C

## 5.6 Triage

**TRIAGE is a decision instrument, not a map.** Its ordering must be
deterministic and explainable, never an LLM 'vibe' ranking.

TACTICAL / TRIAGE  
  
!! K2C! H T 310k -27.8  
AS/VEN INTERCEPT HAZARD  
  
-- K1C S F 92k -8.4  
FS/DOR  
  
-- K3M H FC 640k +0.2  
AP/VEN  
  
.. K4O S C 1400k +6.7  
FP/DOR

Candidate deterministic priority order:

1.  Collision/intercept hazard.

2.  Weapons/firing threat, if legitimately known.

3.  High-rate dangerous approach.

4.  Tactically relevant closing contact.

5.  Other tracked contact.

6.  Opening / low-interest contact.

## 5.7 Selected-Contact Telemetry

SELECT K2  
  
RNG 310k km  
RR -27.8 km/s  
BRG 137 deg  
MRK -39 deg  
TRK TACTICAL  
  
CPA 42 km  
TCA 11m 18s  
  
ATT unresolved  
AGE 0.8 s

CPA/TCA appear only when the sensor/navigation solution actually
supports them. Track age is exposed when relevant rather than bloating
every normal row.

# 6. Locked Human-Factors and Epistemic Laws

- Simulation knows physical truth; the player sees only information that
  could have reached them.

- NAV state, sensor observation and fused navigation state are different
  things.

- Never display greater precision than the source or track has earned.

- A plotted position may not be moved to make a label prettier.

- Orientation arrow = nose attitude, never velocity.

- C/O/M = radial relationship only, never total relative velocity.

- Hazard is separate from hostility and allegiance.

- Ephemeris provenance is separate from contact track quality.

- Canonical interface is monospace text, not emoji-dependent and not
  color-dependent.

- Mandatory tactical views must survive approximately 38 columns without
  horizontal scrolling.

- SIDE is secondary; MAIN + TOP + RANGE + CONTACTS are the default.

- COMPACT accelerates comprehension; it does not teach geometry.

- TRIAGE prioritizes action; it does not replace geometry.


- Propulsive acceleration and net acceleration are distinct when gravity/field effects matter; use PACC/NACC rather than an ambiguous ACC.

- Ephemeris source is distinct from NAV reference/frame. `EPH:JPL` does not mean “J2000”; `NAV REF:ECLIPJ2000` does not say where the numbers came from.

- When chronology diverges, SHIP MET / EXT EPOCH / CAUSAL OFFSET are displayed separately.

- Loom route **access** is directional. Do not label the deep substrate itself “asymmetric” merely because A→B is usable and B→A is not yet surveyed/certified.

- Experimental survey displays are labeled `NAV SCHEMATIC — EXPERIMENTAL`. Ad-hoc engineering/debug overlays are labeled `TEST INSTRUMENTATION — NON-HUD`.


# 7. Navigation Provenance Standard

EPH: SPICE  
only if SPICE was actually evaluated  
  
EPH: HORIZONS  
only if Horizons output was actually used  
  
EPH: PDS  
NASA/PDS-generated solution actually used  
  
EPH: MEAN-ELEM  
published mean elements propagated/calculated  
  
EPH: EST  
explicit estimate  
  
EPH: SIM  
deliberately fictional geometry

The standard never upgrades a plausible result into a NASA-grade result
merely because such a source exists in principle.

# 8. Response Back to the Critics

**Bottom line:** the critiques improved the design. They were most
valuable where they attacked contradictions between our stated
principles and our implementation, especially mobile width, provenance,
and presentation-layer overload.

The design challenge also confirmed that no ledger, octant grid or
compact ladder replaces true spatial projections for 3D maneuver.
However, compact orientation and threat-triage instruments are excellent
secondary views and have been incorporated.

**Final answer:** keep the geometry honest, keep the uncertainty
visible, keep the phone display narrow, keep the source provenance
truthful, and let each instrument answer one human question well.

**Status: LOCKED TACTICAL/HUMAN-FACTORS STANDARD v0.3.** Future changes
should be treated as deliberate design changes, not ad hoc formatting
tweaks.
