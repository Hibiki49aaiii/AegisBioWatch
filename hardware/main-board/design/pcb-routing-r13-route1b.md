# PCB routing — Phase 1 r13 route-1b

## Status

`route-1b` is the first **executed-KiCad-clean routing increment** on the recovered-source r13 Main Board.

It intentionally routes only the nPM1300 switching nodes:

- `U2.3 PMIC_SW1 -> L101.1`
- `U2.5 PMIC_SW2 -> L102.1`

Everything else remains unrouted so that each later power-routing increment can be independently validated.

This is **not** a fabrication release and is **not** a complete PCB DRC pass because 184 ratsnest/unconnected items remain.

## Why route-1b replaced the first route attempt

The earlier route-1 prototype attempted SW, VOUT, VSYS, PVSS and NetTie GND escapes simultaneously using 0.50 mm straight/star tracks. On the 0.5 mm-pitch nPM1300 QFN this produced crossing, shorting, clearance, solder-mask-bridge and dangling-via violations.

That prototype is not routing authority.

Route-1b narrows the first proven increment to SW1/SW2 and uses a QFN breakout geometry appropriate to the actual pad pitch:

- short **0.20 mm** neck-down directly out of U2;
- escape outward before changing Y;
- dogleg routing outside the U2 pad row;
- no GND vias before the continuous In1 GND strategy is instantiated;
- no RF, crystal or supplier-gated interface routing.

The 0.20 mm width remains planning geometry. Fabricator rules are not frozen.

## Executed validation

GitHub Actions workflow:

`r13 route1b SW-only validation`

Run:

`31310289217`

Artifact:

`r13-route1b-sw-evidence` / `9037182269`

Executed with KiCad **9.0.9**.

| Check | Result |
|---|---:|
| Rule violations | **0** |
| Unconnected / ratsnest | **184** |
| Source pin/net nodes audited | **268 / 268 PASS** |
| Track segments added | **7** |
| Vias added | **0** |
| Routed nets | `PMIC_SW1`, `PMIC_SW2` |

The validated generated route PCB SHA-256 is:

`be3e4c8abc2245c42dba34b2d5431631be033334405912288ad405c5e846d638`

The same-run source r13 placement SHA-256 is:

`4c92bdc64de30097a6a9c81906c664e5f987a2afcc002eef71131a2721b1a089`

## Exact route seed geometry

### SW1

- U2.3 `(8.9875, 27.75)`
- escape `(8.1875, 27.75)`
- dogleg `(8.1875, 24.126353)`
- L101.1 `(7.514712, 24.126353)`

### SW2

- U2.5 `(8.9875, 28.75)`
- escape `(8.1875, 28.75)`
- dogleg `(8.1875, 30.65)`
- dogleg `(5.824342, 30.65)`
- L102.1 `(5.824342, 31.79391)`

These coordinates are generated from the current AegisBioWatch r13 placement and are not third-party coordinates.

## Next routing increments

Proceed incrementally and require executed KiCad 9.0.9 DRC after each stage:

1. instantiate the continuous In1 GND strategy / keep-out-aware plane and stitching policy;
2. route BUCK VOUT1 / `+1V8` local path;
3. route BUCK VOUT2 / `+3V0` local path;
4. route VSYS/PVDD input decoupling;
5. route PVSS1/PVSS2 local return trees into NT101/NT102;
6. only then add NetTie-to-GND vias into an actual continuous GND reference;
7. continue VBAT / low-speed power, then nRF internal DC/DC, crystals and revision-matched RF placement/routing.

Do not restore the rejected 0.50 mm straight/star route geometry simply to reduce the ratsnest count faster.

## Authority and gates

Nordic nPM1300 QEAA reference layout/current-loop guidance remains the physical-layout authority. The r13 collision-aware placement and route-1b are implementation evidence inside the AegisBioWatch mechanical envelope.

Still gated before manufacturing include J3, J5, J6, battery-pack construction, applicable nPM1300 build-code/errata, critical passive MPN/effective capacitance, final fabricator stack-up, nRF silicon-revision-matched reference layout, final RF impedance geometry and tuning, Bio electrode charging isolation, complete intentional routing, DRC `0 / 0`, DFM and prototype bring-up.
