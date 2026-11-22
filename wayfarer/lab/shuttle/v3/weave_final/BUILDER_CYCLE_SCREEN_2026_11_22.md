ALL bodies. ALL sponsors. 2026-2226.

# Reactorless Builder Tic Tac: one manoeuvre and its reverse

**Status:** fiction-first, NON-CANON (kT/Sol, 2026-11-22). The torch configuration stays as the reference design. RT is used as inspiration, not proof: RT-C1 control geometry, RT-B1 route dependence, RT-D1/D3 common action. This work may belong in the Research Lab's Loom Drive mechanism lane.
**Code:** `builder_cycle_screen.py` → `builder_cycle_screen.json`.

## The hypothesis

The continuous active hull is an M2-compatible interface to relational topography. It changes her ordinary motion by changing her relational configuration ρ. The whole physical/relational system changes correspondingly. Local energy and heat are **not** booked as reactor output.

## The test

- **Manoeuvre:** a field climb of 2 km (0.95 GJ of ordinary work).
- **Two reverses:** the field descent, or field off, fall, and extract the energy (brake, turbine, aerobraking).
- **Repeat:** climb by field, fall and extract, over and over.

| ρ coupling | Result |
|---|---|
| **L0:** ρ keeps no record of the work done | **Free-work cycle.** Extraction is unbounded (1 TJ after 1,000 cycles and rising) while ρ stays reusable. Excluded |
| **L1:** ρ moves in proportion to the net ordinary work, within an accessible range | **Bounded.** Extraction stops at κ·ρ_max (2 TJ in the illustration); then the climb is refused. Reversing by field restores ρ exactly |

## What changes, and what does not return

- **Up by field, down by field:** everything returns, including ρ. No heat is needed.
- **Up by field, down by falling and braking:** her height and speed return, and the world keeps the energy. **ρ does not return.** It holds the record.

## Finding (corrected after Sol's review of 0db5da0)

L1 shows that **one** accounting model excludes free-work cycles. It does **not** show that conservation forces that model. A partner supplying the energy (e.g. the Sun-partner route), a global field state, a nonlinear cost or a finite environmental exchange could do the same.

**Within L1:**
- A climb stores the work as a relational displacement.
- Descending by field gives it back, cool.
- Physical dissipation leaves the record displaced. Route dependence is in the spirit of RT-B1.
- A bounded range acts as a finite source of usable work. Calling it a state variable does not change that: it is a fictional assumption, and no size is set.

## The conceptual gap (stop)

How is a displaced ρ restored?
- If **only the reverse field manoeuvre** restores it, every aerobraked landing spends range for good: a finite lifetime budget.
- If **the environment relaxes it**, that relaxation must itself be paid physically, or the free-work cycle reopens.

Nothing in RT decides which.

## Flight picture (if adopted as fiction)

- She climbs and accelerates with no propellant and no reactor heat.
- She comes home **by field, unwinding**, to keep her range.
- Every time she sheds energy into the world (aerobraking, braking, drag), that much range is spent until it is restored.
- **One Builder parameter, κ·ρ_max, sets what she can do.**
