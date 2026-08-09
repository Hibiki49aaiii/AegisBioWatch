# PCB placement implementation — Phase 1 r13

## Status

r13 is the current nPM1300 placement implementation. It is generated from the **recovered r8-equivalent topology + r10 mechanical floorplan**, through an executed-KiCad-clean recovered r11 seed.

The historical compressed r7/r11 payloads in Git are truncated and are not used as authority. No byte-identical recovery claim is made.

Current executed placement gate:

- KiCad CLI: **9.0.9**
- components: **79**
- footprints: **76**; J3/J5/J6 intentionally absent
- nets: **86**
- physical pin/net audit: **268 / 268 PASS**
- r13 placement rule violations: **0**
- r13 placement unconnected/ratsnest: **186**

`186` means the placement is still unrouted. It is not a complete PCB DRC pass and is not manufacturing authority.

## Authority

Physical-layout authority for the PMIC block remains Nordic Semiconductor documentation, especially the current nPM1300 QEAA reference layout / hardware guidance. The reviewed QEAA reference-layout v1.2 includes the PVSS1/PVSS2-to-GND NetTie treatment used by this design.

The earlier `hlord2000/nPM1300-Stamp` remains a density/adjacency sanity check only. No third-party absolute coordinates are copied.

## Recovered electrical source

`tools/recover-r8-netlist-from-legacy.py` deterministically reconstructs PCB-stage topology from retained project evidence:

- five retained legacy Eeschema sheets;
- retained AegisBioWatch legacy symbol library;
- retained r8 BOM;
- documented r8 J8/J9 interface freeze;
- documented net-name normalization.

The recovery fails closed unless it reproduces the independently retained invariants:

- 79 components;
- 86 PCB nets;
- 268 logical pin/net nodes;
- critical U1/U2 pin mappings;
- 12 r8 interface checks.

`tools/rebuild-pcb-r11-recovered.py` then constructs the unrouted real-net board inside the actual r10 41 × 34 mm Edge.Cuts and is accepted only after KiCad 9.0.9 reports **0 rule violations / 186 unconnected** plus a **268/268 physical-pad audit**.

## nPM1300 placement method

`tools/materialize-pcb-r13-recovered.py` binds itself to the exact recovered-r11 PCB SHA and executed validation evidence.

U2 remains fixed. Only the 24 PMIC support references are repositioned:

- C101–C114
- L101/L102
- NT101/NT102
- R101–R106

Non-PMIC seed references are not moved.

Placement uses:

- actual AegisBioWatch U2 and inductor pad coordinates;
- actual KiCad no-text footprint bounding geometry;
- 0.10 mm planning collision gap;
- functional attraction toward the relevant PMIC pins/nets;
- bounded legalization when a preferred location is physically blocked.

The high-current SW/PVDD/PVSS/VOUT group is placed before lower-current VSET/I2C/LS-LDO support circuitry. In the validated implementation only C104 and L102 required the bounded legalization expansion.

This is an implementation of reference-layout intent inside the AegisBioWatch envelope, not a copy of reference-board coordinates.

## Ground and PVSS policy

- In1.Cu role remains one continuous GND reference; the GND plane is not split.
- PVSS1_LOCAL and PVSS2_LOCAL are local switching-return nets.
- NT101/NT102 are the explicit transition points from those local returns to the continuous GND system.
- NetTie-to-GND vias must not be treated as complete until an actual keep-out-aware In1 GND plane/stitching implementation exists.

## Routing status

The first over-broad routing prototype is rejected: it attempted several power loops simultaneously with 0.50 mm straight/star tracks and produced KiCad geometry violations.

The accepted first routing increment is **route-1b**, documented in `pcb-routing-r13-route1b.md`:

- PMIC_SW1 and PMIC_SW2 only;
- 0.20 mm QFN neck-down;
- dogleg escape outside the 0.5 mm-pitch U2 pad row;
- 7 segments;
- 0 vias;
- KiCad 9.0.9 rule violations = **0**;
- unconnected = **184**;
- physical pin/net audit = **268 / 268 PASS**.

Continue routing incrementally, with executed KiCad DRC after every stage. Do not restore the rejected straight/star geometry merely to reduce ratsnest count.

## Current reproduction path

```bash
python3 tools/recover-r8-netlist-from-legacy.py
python3 tools/rebuild-pcb-r11-recovered.py \
  --netlist hardware/main-board/kicad/recovered-r8/AegisBioWatch-MainBoard-r8-recovered.xml
```

After the r11 executed DRC/pad-audit evidence is available:

```bash
python3 tools/materialize-pcb-r13-recovered.py \
  --drc-summary <r11-drc-summary.json> \
  --pin-net-audit <r11-pin-net-audit.json>
```

Route-1b is then generated from the exact validated r13 placement by:

```bash
python3 tools/materialize-pcb-r13-route1b-recovered.py \
  --placement-drc-json <r13-drc.json> \
  --placement-pin-net-audit <r13-pin-net-audit.json>
```

The durable validation workflow is `.github/workflows/r13-route1b-sw-validation.yml`.

## Next routing increments

1. establish the keep-out-aware continuous In1 GND plane/stitching strategy;
2. BUCK VOUT1 / +1V8 local output path;
3. BUCK VOUT2 / +3V0 local output path;
4. VSYS/PVDD input decoupling;
5. PVSS1/PVSS2 local return trees to NT101/NT102;
6. NetTie-to-GND vias into the actual continuous GND plane;
7. VBAT / charger power;
8. nRF internal DC/DC and crystals;
9. revision-matched RF matching/feed after silicon revision and fab stack-up gates close;
10. remaining buses/GPIO/debug.

## Unchanged release gates

Still blocked before manufacturing include J3 watch contact land/mechanics, J5 official AMOLED FPC pinout, J6 touch physical/electrical definition, protected battery-pack construction, applicable nPM1300 build-code/errata, critical passive MPN/effective capacitance, final fabricator stack-up, nRF silicon-revision-matched reference design, final 50-ohm geometry and VNA tuning, Bio electrode charging isolation, complete intentional routing, KiCad **rule violations = 0 / unconnected = 0**, DFM and Rev.0 bring-up.

## Privacy boundary

Repository material is restricted to engineering abstractions. It contains no individual health history, private messages, medication names/doses, or identifiable health information.
