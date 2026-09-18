---
title: LOOM Style Guide
version: 0.1.0-draft
status: DRAFT
approved: false
tokens: loom-tokens.json
manifest: loom-tokens.json ($manifest)
files: 7 (see section 9)
---

# LOOM Style Guide

> **Status: DRAFT v0.1.0. Not approved.** Values marked *proposed* or *observed* are not on the
> brand sheet and need owner approval (section 7). Until approval is recorded in
> `loom-tokens.json` (`$manifest`), treat every existing token as fixed unless the owner asks for a change.

**Audience.** People and coding agents (Codex and others). Rules use MUST / MUST NOT / SHOULD.
**Source of truth.** `loom-tokens.json` holds every value. This document explains meaning and usage; if the two
disagree, the tokens win and this document has a bug.

## 0. How to use this system

1. Never type a colour, size or font by hand if a token exists. Use `loom-tokens.css` (web) or
   `loom_design.py` (Python).
2. Pick the layer first (section 1), then the token.
3. Run `python loom_design.py` after any token or asset change (add `--report` for the contrast report).

Provenance tags used throughout:

| Tag | Meaning |
|---|---|
| `source` | Read directly from the owner's brand sheet (palette, typography, logo image). |
| `observed` | Seen in the brand sheet or the owner's Ceres Atlas mock but not stated as a rule. |
| `derived` | Computed from source values (alpha variants of brand colours). |
| `proposed` | New here. Needs approval. |

## 1. Three layers

| Layer | Owns | Token prefix | May reference |
|---|---|---|---|
| **Brand** | Logo, Montserrat, primary/accent/secondary palette, document identity | `brand.*` | nothing |
| **Interface** | Panels, HUD typography, controls, selection, density, motion | `interface.*` | brand |
| **Domain** | Operational meaning: status, data certainty, navigation states | `domain.*` | brand, interface |

Rules:

* **L1.** A lower layer MUST NOT reference a higher one (enforced by the validator).
* **L2.** Brand colours carry identity, never operational meaning. An accent is not a status.
* **L3.** A domain colour MUST correspond to a defined operational condition (section 4.1). Warning orange is a
  condition, not "a nice orange".
* **L4.** Interface improvements MUST NOT silently change brand values. Brand changes need approval and a version bump.

## 2. Brand layer

### 2.1 Identity

| Item | Value |
|---|---|
| Name | LOOM |
| Tagline | A BRIGHTER UNIVERSE CONNECTS US |
| Supporting lines | A COHERENT UNIVERSE. A CLEARER TOMORROW. / FURTHER TOGETHER / CIVILIZATION BEYOND BORDERS / SAME STARS. A RICHER TOMORROW. |
| Product lockup | LOOM / ATLAS (wordmark, then product name in ion-blue, uppercase label style) |
| One-line abstract | Hard-science-fiction worldbuilding and systems platform for human civilization across the Solar System: navigation, atlas, infrastructure, economic and societal views in one coherent future-operating picture. |

Tagline and supporting lines are uppercase, `label` role, ion-blue or steel, never inside the logo.

### 2.2 Logo

Logo files (same folder as this guide):

| File | Use |
|---|---|
| `loom-wordmark-white.svg` | Default. On void, deep-space, midnight, slate, nebula, photography. |
| `loom-wordmark-void.svg` | On light backgrounds and print. |
| `loom-mark-ion-blue.svg` | Icon, favicon, loading indicator, on dark surfaces. For monochrome use, change the stroke to white or void (nothing else). |

Construction (measured from the brand sheet; see D5):

* Geometric, single-weight strokes. Stroke ≈ 7% of the O diameter. Square (butt) stroke ends.
* **L**: vertical stem with a foot to the right. **O**: full ring. **O**: ring segmented into four arcs, with a small
  gap at north, east, south and west. **M**: two vertical stems and a V that descends about 60% of the cap height.
* Letterspacing is wide (roughly 0.7 to 0.8 × the O diameter between letters). Do not tighten it.

Usage:

* **B1.** Use the supplied SVGs. MUST NOT retype the logo in Montserrat or any other font.
* **B2.** Clear space on all sides ≥ 0.5 × wordmark height (`brand.logo.clear-space-ratio`).
* **B3.** Minimum size on screen: wordmark 96 px wide, mark 16 px (`brand.logo.min-*`).
* **B4.** Colours: white, void, or (mark only) ion-blue. No gradients, glows, outlines, drop shadows, other accents.
* **B5.** MUST NOT stretch, rotate, close the gaps in the segmented O, or place the logo over busy imagery without a
  scrim that keeps ≥ 4.5:1 behind it.
* **B6.** The segmented O may stand alone as the mark; the plain O may not.

### 2.3 Colour

All hex values are `source` unless noted. Contrast is measured against `void` (#05070B) for reference; the full
matrix comes from `python loom_design.py --report`.

**Primary: background / UI base**

| Token | Name | Hex | Role |
|---|---|---|---|
| `brand.color.primary.void` | Void | `#05070B` | Page canvas |
| `brand.color.primary.deep-space` | Deep Space | `#0B1220` | Panel |
| `brand.color.primary.midnight` | Midnight | `#11182B` | Raised panel |
| `brand.color.primary.slate` | Slate | `#1E2A3A` | Controls, tracks |
| `brand.color.primary.nebula` | Nebula | `#22364A` | Highest elevation |

**Accent: pops and interactives (identity, not status)**

| Token | Name | Hex | Role | On void |
|---|---|---|---|---:|
| `brand.color.accent.ion-blue` | Ion Blue | `#00D1FF` | Interactive, labels, links, focus of action | 11.1 |
| `brand.color.accent.amber` | Amber | `#FF8703` | Hero metric (see D1) | 8.4 |
| `brand.color.accent.crimson` | Crimson | `#FF3B3B` | Identity accent only | 5.7 |
| `brand.color.accent.violet` | Violet | `#B96BFF` | Secondary interactive, alternates | 6.3 |
| `brand.color.accent.emerald` | Emerald | `#00E676` | Identity accent only | 12.1 |

**Secondary: support**

| Token | Name | Hex | Role | On void |
|---|---|---|---|---:|
| `brand.color.secondary.steel` | Steel | `#8A97A6` | Tertiary text, unresolved data | 6.8 |
| `brand.color.secondary.ice` | Ice | `#C7D3DF` | Secondary text and icons | 13.3 |
| `brand.color.secondary.sand` | Sand | `#D6B98A` | Warm neutral; provisional data | 10.7 |
| `brand.color.secondary.copper` | Copper | `#C47F46` | Environmental / infrastructure detail | 6.2 |
| `brand.color.secondary.mint` | Mint | `#7EE7D1` | Environmental detail | 13.7 |

**Neutral (observed)**: `brand.color.neutral.white` `#FFFFFF`, logo and primary text (D6).

Rules:

* **C1.** The UI is dark-only. Do not build a light theme without approval.
* **C2.** Text sits on `canvas` through `highest` surfaces only. Steel MUST NOT be used as text on nebula (4.17:1).
* **C3.** Crimson, emerald, amber and mint MUST NOT be used for anything a viewer could read as status (L2, D1, D2).
* **C4.** Do not introduce new hues. If a design need cannot be met, raise it as a decision (section 7).

### 2.4 Typography

Typeface: **Montserrat** only (SIL OFL 1.1). No italics; no weight above 500. Font file status: see Appendix B (D10).

| Role | Token base | Weight | Tracking | Case |
|---|---|---|---|---|
| Display / hero | `brand.font.role.display` | ExtraLight 200 | +200 (0.2em) | UPPERCASE |
| Section / subhead | `brand.font.role.subhead` | Light 300 | +100 (0.1em) | UPPERCASE |
| Body copy | `brand.font.role.body` | Regular 400 | 0 | Sentence case, clean and legible |
| Labels / UI / navigation | `brand.font.role.label` | Medium 500 | +80 (0.08em) | UPPERCASE (tabs, buttons, data labels) |

Fallback stack (load failure only): Montserrat, Avenir Next, Segoe UI, Roboto, system-ui, sans-serif.

* **T1.** Tracking applies to uppercase roles only. Body copy is never tracked.
* **T2.** Do not fake weights (no synthetic bold). Use the four weights above.
* **T3.** Use the supplied logo SVG for the logo, Montserrat for everything else.

## 3. Interface layer

### 3.1 Surfaces and elevation

Elevation is expressed by lightness, then by the hairline border, never by heavy shadow.

| Token | Value | Use |
|---|---|---|
| `interface.surface.canvas` | void | Page |
| `interface.surface.panel` | deep-space | Default panel |
| `interface.surface.raised` | midnight | Panel in panel; hover |
| `interface.surface.control` | slate | Bar tracks, inset regions |
| `interface.surface.highest` | nebula | Pressed control |
| `interface.border.hairline` | ion-blue 18% | Panel edge |
| `interface.border.divider` | steel 25% | Data-row dividers |
| `interface.border.default` / `.strong` | ion-blue 35% / 100% | Control rest / selected |

Panels: `radius.panel` 12 px, 1 px hairline border, `space.4` padding. Frames around imagery: `radius.frame` 8 px.

### 3.2 Text colour and permitted pairings

| Token | Colour | Use | Allowed surfaces |
|---|---|---|---|
| `interface.text.primary` | white | Headings, key values | all |
| `interface.text.secondary` | ice | Supporting copy | all |
| `interface.text.tertiary` | steel | Footnotes, captions | canvas, panel, raised, control |
| `interface.text.label` / `.value` / `.link` | ion-blue | Labels, tabulated values, links | all |
| `interface.text.hero-metric` | amber | Atlas headline metric only (D1) | all |
| `interface.text.on-accent` | void | Text on solid ion-blue | ion-blue fill |
| `interface.text.disabled` | steel 55% | Disabled; must also carry a non-colour cue | any |

Measured contrast (WCAG, higher is better; text needs 4.5, graphics 3):

| Foreground | canvas | panel | raised | control | highest |
|---|---:|---:|---:|---:|---:|
| white | 20.2 | 18.7 | 17.7 | 14.5 | 12.4 |
| ice | 13.3 | 12.3 | 11.6 | 9.5 | 8.2 |
| steel | 6.8 | 6.3 | 5.9 | 4.9 | **4.2 (fails)** |
| ion-blue | 11.1 | 10.3 | 9.7 | 8.0 | 6.8 |
| amber | 8.4 | 7.8 | 7.3 | 6.0 | 5.2 |
| status critical `#EF4444` | 5.4 | 5.0 | 4.7 | **3.9 (graphics only)** | **3.3 (graphics only)** |

The validator re-computes 74 pairs on every run and fails the build if any drops below its minimum.

### 3.3 Type styles

Sizes are `proposed` (sized for a phone-width HUD); weight, tracking and case come from the brand roles. Apply with the
CSS class `loom-type-<name>` or `loom_design.type_style("<name>")`.

| Style | Size / line-height | Role | Example |
|---|---|---|---|
| `display` | 40 / 1.1 | Display | CERES |
| `hero-metric` | 32 / 1.1, Light, tabular | none (Light, untracked) | 5.508T / year |
| `title` | 18 / 1.25 | Subhead | THE ECONOMY |
| `subhead` | 14 / 1.25 | Subhead | EXPLORE FURTHER |
| `body` | 14 / 1.5 | Body | Sentences |
| `data` | 14 / 1.4, tabular | Body | 452,034 |
| `control` | 12 / 1.1 | Label | ECONOMY (chips, tabs, buttons) |
| `label` | 11 / 1.4 | Label | RESIDENT POPULATION |
| `caption` | 12 / 1.4 | Body | Footnotes |

* **T4.** 11 px (`label`) is the floor for any text. Below 360 px viewport width `display` drops to 32 px.
* **T5.** Numbers in columns, tables and bars MUST use tabular figures (`font-variant-numeric: tabular-nums`). Verify glyph support once the font file is present.
* **T6.** Line length for body copy SHOULD stay under 70 characters.

### 3.4 Spacing, shape, targets

* Spacing scale (4 px base): `space.1`…`space.8` = 4, 8, 12, 16, 24, 32, 48, 64 px. Use only these.
* Radii: `bar` 2, `frame` 8, `panel` 12, `pill` 999 (chips, tabs, badges).
* **S1.** Interactive targets MUST be at least `size.target-min` (44 px) in both axes. The Pixel phone is a first-class target.
* **S2.** Narrowest supported layout is 360 px wide, single column, gutters `size.gutter` (16 px). No horizontal page scroll; wide tables scroll inside their own container.

### 3.5 Controls and states

Chip / tab / button pattern (from the Ceres mock):

| State | Background | Border | Text | Extra |
|---|---|---|---|---|
| Rest | panel | ion-blue 35% | ice | none |
| Hover | raised | ion-blue 35% | ice | none |
| Selected | ion-blue 14% | ion-blue | ion-blue | `effect.glow-active`; `aria-pressed`/`aria-current` set |
| Pressed | nebula | ion-blue | ion-blue | none |
| Disabled | panel | divider | disabled | not focusable, `aria-disabled` |
| Focus (keyboard) | unchanged | unchanged | unchanged | 2 px white ring, 2 px offset |

* **I1.** Selected state MUST be conveyed by more than colour: the accessible state attribute plus border weight/fill change (glow is decoration only).
* **I2.** The keyboard focus ring is white and MUST always be visible. It is deliberately not ion-blue so it can never be mistaken for "selected".
* **I3.** The 35% rest border is decorative (≈ 2.2:1 on panel). The control is identified by its label and 44 px target, so a visible text label is mandatory (no icon-only chips).
* **I4.** In running text, links MUST be underlined or otherwise non-colour distinguished.

### 3.6 Data visualisation

* Bars: 10 px high, `radius.bar`, track `dataviz.bar-track`, primary fill ion-blue, secondary steel. Show the value as text beside the bar. A bar is never the only carrier of a number.
* Multi-series charts use `dataviz.series-1…6` in order (ion-blue, violet, sand, mint, ice, copper). Amber and every status colour are excluded. Every series MUST also have a direct label or a distinct marker/dash.
* Stacked versus distinct flows: never stack quantities that are different kinds of annual flow (the Ceres mock states this explicitly for value added versus investment).
* Show units and time base in the value (`5.508T / yr`), and show provisional, estimated or unresolved values with the certainty treatment in section 4.3.

### 3.7 Motion

`motion.duration-fast/base/slow` = 120 / 200 / 400 ms, `easing-standard` cubic-bezier(0.2, 0, 0, 1).
Motion answers an action (selection, expand, confirm). No decorative looping motion. The generated CSS sets all durations to 0 under
`prefers-reduced-motion: reduce`; non-CSS renderers MUST honour the platform equivalent.

### 3.8 Layout pattern (Atlas dossier)

Single column. Order used in the Ceres mock: product lockup and location breadcrumb, image frame, body name (`display`), one-line descriptor, four headline stats (2 × 2), analytical navigation chips, then panels each headed by a `title` and a scope badge, ending with a schematic index and the footer line. Hairline dividers separate sections. Keep this order for other bodies unless there is a reason to change it.

## 4. Domain layer

### 4.1 Status registry

Status colours are the semantic row of the brand sheet, renamed for operational meaning. Hex values are unchanged.

| Status | Token base | Colour | Shape | Icon | Label | Severity | Defined condition |
|---|---|---|---|---|---|---:|---|
| Nominal | `domain.status.nominal` | `#22C55E` (sheet: Success) | circle | check in circle | NOMINAL | 0 | Inside its defined nominal envelope. |
| Info | `domain.status.info` | `#38BDF8` (sheet: Info) | square | i in square | INFO | 1 | Informational. No action implied. |
| Caution | `domain.status.caution` | `#F59E0B` (sheet: Warning) | triangle | ! in triangle | CAUTION | 2 | A defined limit is approached or a margin is reduced. |
| Critical | `domain.status.critical` | `#EF4444` (sheet: Danger) | octagon | ! in octagon | CRITICAL | 3 | A defined limit is breached or a safety-relevant fault exists. |

Selection highlight `#FDE047` (`domain.selection.highlight`) is **not** a status. It marks focus of attention (ring or underline plus a label/position cue) and carries no severity.

Rules:

* **D-S1. Bind to conditions.** A system MUST NOT render a status unless it can name the governing condition that produced it (the `threshold-source`). Every status is currently `UNDEFINED`: **no threshold, reserve or limit is defined by this design system.** Owners of each subsystem define theirs and reference them.
* **D-S2. Redundancy.** Every status is rendered with colour + shape + label. Colour alone is never sufficient. A red line alone MUST NOT be the only way to distinguish a critical navigation state. Add the octagon marker, the CRITICAL label, and a stroke difference.
* **D-S3. Order.** Severity ordering is nominal < info < caution < critical. Sort and escalate by `severity`, never by hue.
* **D-S4. Colour separation.** Status hues MUST NOT be reused for identity, decoration, series, or badges (L2, C3).
* **D-S5. Assistive tech.** Announce the label and condition text (`role="status"` or `role="alert"` for critical), not the colour.

### 4.2 Colour-vision accessibility (measured)

The validator simulates protanopia, deuteranopia and tritanopia and reports colour separation (CIE76 ΔE; below 20 is unreliable).
Pairs that are **not** reliable by colour alone (from `python loom_design.py --report`):

* nominal / critical under deuteranopia (ΔE 13): the red-green case.
* nominal / info under tritanopia (ΔE 14).
* caution / selection under deuteranopia (ΔE 16): yellow versus amber, one more reason selection is a ring and not a fill.

Also: the brand accents sit very close to the status colours (amber vs caution ΔE 16, crimson vs critical ΔE 11, emerald vs nominal ΔE 14, ion-blue vs info ΔE 13). This is why accents must never appear in status contexts.

Minimum accessibility standard for anything built on this system:

* **A1.** Text contrast ≥ 4.5:1 (≥ 3:1 for text ≥ 24 px, or graphics and UI boundaries that carry meaning).
* **A2.** Never encode meaning by colour alone: pair with shape, label, position, dash or icon.
* **A3.** Focus always visible (I2). Targets ≥ 44 px (S1).
* **A4.** Respect reduced motion (3.7). Respect system text size where the platform provides it.
* **A5.** Test each new domain view in greyscale. If two states look identical, the design is wrong.

### 4.3 Data certainty

LOOM's atlas shows values whose reliability differs (the Ceres mock flags unresolved definitions and NULL fields). Uncertainty MUST NOT borrow status colours, so it can never be mistaken for severity.

| State | Colour | Line dash | Text affix | Label |
|---|---|---|---|---|
| Verified | white | solid | none | VERIFIED |
| Provisional | sand | `6 4` | suffix `(P)` | PROVISIONAL |
| Estimated | ice | `2 3` | prefix `≈` | ESTIMATED |
| Unresolved | steel | `1 4` | suffix `?` | UNRESOLVED |
| Null | steel | `1 4` | replaces value with `—` | NULL |

* **D-C1.** A NULL is shown as NULL. Never render it as zero, blank, or an interpolated number.
* **D-C2.** If a headline value is unresolved or provisional, its state shows next to it, not in a tooltip.

### 4.4 Navigation and spatial states

Every state differs in colour **and** stroke **and** marker, so they survive greyscale (validator-enforced).

| State | Token | Colour | Width | Dash | Marker |
|---|---|---|---:|---|---|
| Orbit | `domain.nav.orbit` | steel | 1 | `4 6` | none |
| Node | `domain.nav.node` | ice | 1 | solid | filled circle |
| Selected node | `domain.nav.node-selected` | highlight | 2 | solid | ring around node |
| Planned route | `domain.nav.route-planned` | ion-blue | 2 | `6 4` | open circle |
| Committed route | `domain.nav.route-committed` | ion-blue | 3 | solid | filled circle |
| Alternate route | `domain.nav.route-alternate` | violet | 2 | `2 4` | diamond |
| Completed route | `domain.nav.route-completed` | steel | 2 | solid | check |
| Keep-out region | `domain.nav.keep-out` | critical | 2 | solid | hatch fill + KEEP-OUT label |

`orbit` and `node` are `observed` from the Ceres schematic; the rest are `proposed`.
Keep-out uses the critical colour because it represents a critical condition, so it inherits D-S1.

### 4.5 Reserved, not yet defined

Actor-relationship encoding, population overlays, and hazard/alert taxonomy beyond the four statuses. Do not invent them ad hoc; propose them under section 7.

## 5. Document identity

* Use the wordmark top-left, with the product lockup on the right (`LOOM / ATLAS`).
* Section headings use `title`/`subhead` styles; labels above stats use `label` in ion-blue.
* Footer line: the tagline family, `label` style, steel, hairline rule above.
* Cover and hero imagery: real-looking hard-SF stations, ships and planetary surfaces in cool blue-grey with warm orange practical lights, no cartoon styling. Keep imagery behind a scrim wherever text overlaps.

## 6. Adapters and validation

| Technology | Adapter | How |
|---|---|---|
| Web / HTML / Android WebView | `loom-tokens.css` (generated; includes `@font-face`) | Link it; use `var(--loom-…)` and `.loom-type-*`. |
| Python (Pygame, Pillow, Rich, Termux) | `loom_design.py` | `get()`, `rgb()`, `ansi_fg()`, `status()`, `type_style()`. Stdlib only. |
| Other renderers | Tokens JSON (DTCG-style) | Write a small adapter; do not copy hex values. |

`python loom_design.py` checks: JSON validity, token types and values, alias resolution, layer direction, provenance tags, duplicate colours, alpha colours derive from the palette, status/certainty/navigation distinguishability, 74 contrast pairs, asset presence and SVG well-formedness, manifest status. It regenerates `loom-tokens.css`. `--check` fails if that file is stale (use in CI). `--report` prints the contrast and colour-vision tables.

Current warnings are expected: the Montserrat file is not bundled (D10), and status thresholds are `UNDEFINED` (D-S1).

## 7. Decisions needed before APPROVED

| ID | Decision | Recommendation |
|---|---|---|
| D1 | The Ceres mock shows the hero metric in amber `#FF8703`, which sits ΔE 16 from the caution colour `#F59E0B`. A viewer could read a headline number as a caution. | Keep amber only for the single Atlas hero metric, never near status, or move the hero metric to white. Owner to choose. |
| D2 | The mock's `BODY + NODES` badge is green (an accent used like a status). | Restyle scope badges in ion-blue outline. Reserve green for NOMINAL. |
| D3 | Brand sheet sets navigation/tabs/buttons in Medium uppercase +80. The mock's chips are sentence-case regular. | This guide follows the sheet. Confirm, or amend the sheet. |
| D4 | The mock's section titles look more widely tracked than the sheet's +100. | This guide follows the sheet (`title` uses +100). |
| D5 | The logo SVGs were reconstructed by measuring the sheet raster. | Replace with the master vector if one exists; otherwise approve as the master. Clear space and minimum sizes are proposals. |
| D6 | White `#FFFFFF` is used for the logo and headings but is not on the palette sheet. | Add to the palette. |
| D7 | Sheet names Success/Warning/Danger were renamed nominal/caution/critical; hex values unchanged. | Approve the rename; owner of each subsystem defines thresholds (D-S1). |
| D8 | Sheet tracking values (+200, +100, +80) are interpreted as thousandths of an em. | Confirm the unit. |
| D9 | The segmented O is promoted to a standalone mark. | Approve or drop `loom-mark-*.svg`. |
| D10 | Montserrat font binary not bundled. | Add per Appendix B. |

## 8. Change control

* States: `DRAFT` (now), then `APPROVED` once the owner records approval in `loom-tokens.json` under `$manifest.approval` (`approved_by`, `approved_on`, `approved_version`). The validator enforces consistency.
* Versioning (SemVer): **MAJOR** = change to an approved brand value, logo geometry, or a domain status meaning. **MINOR** = new token, new state, new adapter. **PATCH** = documentation or validation fixes.
* Interface-layer changes after approval need a stated reason and MUST NOT alter brand or domain tokens. Domain changes need a defined operational condition first.
* Never edit `loom-tokens.css` by hand; regenerate it.

## 9. Package map (7 files)

| File | Purpose |
|---|---|
| `LOOM_STYLE_GUIDE.md` | This document, including the AGENTS.md snippet (Appendix A) and font install (Appendix B). |
| `loom-tokens.json` | All tokens (`brand`, `interface`, `domain`, DTCG-style) plus `$manifest`: version, DRAFT/APPROVED, asset list, contrast checks. |
| `loom-tokens.css` | Generated. CSS custom properties, `.loom-type-*` classes, focus and reduced-motion rules, `@font-face`. |
| `loom_design.py` | Python adapter, validator and CSS generator, stdlib only. |
| `loom-wordmark-white.svg` | Logo for dark backgrounds. |
| `loom-wordmark-void.svg` | Logo for light backgrounds. |
| `loom-mark-ion-blue.svg` | Segmented-O mark. |

The owner's original brand sheet and Ceres Atlas mock are the reference images for every `source` and `observed` tag. They are not bundled; keep the originals.

## Appendix A. Paste into the repository root AGENTS.md

```markdown
## LOOM design system

Status: DRAFT (`$manifest` in `loom-tokens.json`). Sources of truth: `LOOM_STYLE_GUIDE.md` and `loom-tokens.json`.
(If the files live in a subfolder such as `design/`, prefix the paths below.)

When you build or change any UI, HUD, chart, document or image, or use the logo:

- Read `LOOM_STYLE_GUIDE.md` (sections 1, 3, 4) first.
- Use tokens. Never write literal hex, font or spacing values that exist as tokens.
  Web: `loom-tokens.css`. Python: `loom_design.py`.
- Layers: brand, then interface, then domain. A lower layer never references a higher one. Brand colours carry identity, not meaning.
- Status colours (nominal, info, caution, critical) mean a defined operational condition and are always shown with shape and label. Never encode meaning by colour alone.
- Do not invent thresholds or limits for a status. Cite the governing spec for the system that produces it.
- Data certainty (verified, provisional, estimated, unresolved, null) never uses status colours. Show NULL as NULL, never as zero or blank.
- Logo: use the SVG files. Never retype it in a font.
- Accessibility floor: 4.5:1 text contrast, 3:1 for graphics, 44 px touch targets, visible keyboard focus, reduced motion respected.
- Do not edit the tokens, logo SVGs or the generated CSS unless the task is explicitly about the design system. If a needed token is missing, say so and propose it; do not improvise a value.
- After touching any of these files run `python loom_design.py` (CI: add `--check`).
```

Rules for editing the design system itself:

* Existing token values are fixed unless the task says to change them. New tokens are tagged `proposed`.
* Every token needs a provenance tag. Reuse by alias (`{brand.color.accent.ion-blue}`); do not duplicate a hex value. Alpha variants must derive from a brand palette colour and be tagged `derived`.
* A new status colour, or a new meaning for one, needs a written operational condition first (section 4.1), plus a distinct shape and label.
* Status, certainty and navigation states must stay distinguishable without colour (validator-enforced).
* After every change: run `python loom_design.py`, update any table in this guide that quotes a changed value, and add open questions to section 7.
* The logo SVGs are geometry, not text. If the geometry changes, record it in D5.

## Appendix B. Montserrat font install

The font binary is not bundled (no network when this was assembled).

1. Download Montserrat (variable) from Google Fonts or `github.com/JulietaUla/Montserrat`. Licence: SIL Open Font License 1.1 (bundling and embedding allowed).
2. Convert to WOFF2 if needed: `pip install fonttools brotli`, then `fonttools ttLib.woff2 compress "Montserrat[wght].ttf" -o Montserrat-VF.woff2`.
3. Save it as `Montserrat-VF.woff2` beside `loom-tokens.css` and keep the OFL licence text with it.
4. Run `python loom_design.py`; the "font file not present" warning disappears.

Weights used: ExtraLight 200 (display), Light 300 (subhead), Regular 400 (body), Medium 500 (labels/UI). No italics, nothing above 500.

* Pillow/Pygame: load the variable TTF and set the weight axis (for example `ImageFont.truetype(path).set_variation_by_axes([300])`); read weights from `loom_design.get("brand.font.weight.light")`.
* Terminals/Termux use the terminal's own font: apply colour, uppercase labels and hierarchy only, no letter-spacing.
* Android WebView falls back to Roboto if the file is absent; layout must still hold (rule S2).
* Verify tabular figures (`font-variant-numeric: tabular-nums`) and the symbols `≈` and `—` render once the font is in place.
