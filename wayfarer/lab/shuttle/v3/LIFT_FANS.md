# Shuttle v3: electric fans + house reactor (option 1 sizing)
ALL bodies. ALL sponsors. 2026-2226. NON-CANON screen. `lift_fans.py` → `lift_fans.json`, `lift_fans.png`.

- **1a, hover on Earth:** fans carrying the full ~59 t landing mass need 100–200 MWe → **13–22 t added**. Busts the 52.5 t ceiling. Claude's earlier "+5–7 t" guess (chat 2026-11-21) was wrong; motors dominate.
- **1b, ~8–10 m² of fans and a ~28 MWe reactor: +3.4–3.6 t.** Earth: takes off and lands on water or a runway (hump drag ~0.25 W) and flies on reactor power (~17 MWe at 100 m/s, L/D 5), using no water. Titan: true hover (~4 MW). Venus with the kit: true hover (~28 MW), so it may retire the kit rotor, tipjets and kit reactor (5.8 t), OPEN on fans and motors at 737 K. Vertical landing on land on Earth stays on the belly rockets.
- Reactor waste heat (~9 MW) goes into the fan air; in vacuum the reactor idles at its 10% minimum.
- Assumptions are labelled in the script: motors 20 kW/kg, figure of merit 0.78, fans 60 kg/m², reactor scaled from the kit's 3.095 t / 75 MWe.
