# PCB routing seed — Phase 1 r13 route-1

## Status

**Implementation prepared / execution gated by KiCad placement DRC / not manufacturing release.**

Route-1 starts copper only for the nPM1300 critical local power loops. It deliberately excludes U1 RF/crystals, unresolved display/touch interfaces, the magnetic-dock land pattern, and Bio Board safety-critical interfaces.

## Mandatory entry gate

`tools/materialize-pcb-r13-route1.py` first regenerates the r13 placement, then refuses to add copper unless all of the following agree:

- executed KiCad version contains **9.0.9**;
- placement rule violations = **0**;
- placement unconnected items = **186**;
- the packaged placement result is marked `EXECUTED_KICAD_CLI`;
- the freshly generated placement PCB SHA-256 exactly matches the PCB SHA stored in that executed result;
- the supplied DRC JSON SHA-256 exactly matches the DRC SHA stored in that executed result.

The 186 count is the known r11/r13 placement-only topology baseline. The SHA binding prevents stale KiCad evidence from authorizing routing on a different placement build.

## Route-1 scope

The routing seed adds only:

1. U2 SW1 → L101
2. U2 SW2 → L102
3. L101 → C107 on the local +1V8 output node
4. C107 → U2 pin 1 `VOUT1`
5. L102 → C108 on the local +3V0 output node
6. C108 → U2 pin 32 `VOUT2`
7. U2 pin 4 `PVDD` / project `VSYS` net → C103 / C104 / C114
8. compact `PVSS1_LOCAL` return tree across U2 / C103 / C107 / NT101
9. compact `PVSS2_LOCAL` return tree across U2 / C104 / C108 / NT102
10. short NT101/NT102 GND-side escapes to provisional through-vias for entry into the continuous board GND system

The VOUT1/VOUT2 connections are mandatory parts of the regulated output nodes; Nordic defines QFN32 pin 1 as `VOUT1`, pin 4 as BUCK `PVDD`, and pin 32 as `VOUT2`.

The PVSS return tree is generated from actual pad coordinates with a small Euclidean minimum-spanning tree. This minimizes local-return track length without importing third-party coordinates.

## Routing-seed geometry

Current seed values:

- SW1/SW2: 0.25 mm
- local VSYS/PVDD: 0.30 mm
- local PVSS: 0.35 mm
- BUCK VOUT local node: 0.35 mm
- NetTie GND escape: 0.30 mm
- provisional through-via: 0.60 mm / 0.30 mm drill

These are **routing-seed values only**. They are not fabrication authority and do not close current-density, thermal, annular-ring, via-aspect-ratio, assembly, or DFM gates.

The final power geometry is frozen only after:

- actual fab minimums/stack-up are known;
- copper weight is known;
- current/transient budget is reviewed;
- KiCad DRC is clean for the intended rules;
- DFM review is complete.

## Ground strategy

- In1.Cu remains one continuous GND plane.
- `PVSS1_LOCAL` / `PVSS2_LOCAL` remain local switching-return nets only around their BUCK loop.
- NT101 / NT102 are the explicit schematic/DRC transition to GND.
- Route-1 does not create a plane split, moat, or isolated analog ground.
- Final NetTie copper/via geometry still requires side-by-side review against the applicable Nordic nPM1300 reference layout.

## Explicit exclusions

Route-1 does **not** route or alter:

- nRF54L15 `ANT` / matching / harmonic-filter network;
- HFXO/LFXO traces;
- nRF DCC/DECD/DECA/DECRF cluster;
- final 50 Ω feed width;
- J3 magnetic dock contact;
- J5 AMOLED FPC;
- J6 touch interface;
- Bio Board electrode paths / charging interlock;
- ordinary GPIO, QSPI, SPI, I2C, interrupts or debug.

## Reproduction

The script expects both the committed/generated executed placement result and its matching raw KiCad DRC JSON. The raw DRC path is supplied through `R13_PLACEMENT_DRC_JSON` or defaults to `/tmp/drc-r13.json`.

```bash
R13_PLACEMENT_DRC_JSON=/tmp/drc-r13.json \
python3 tools/materialize-pcb-r13-route1.py
```

Generated route board:

```text
hardware/main-board/pcb/route-r13-1/AegisBioWatch-MainBoard-Route1-r13.kicad_pcb
hardware/main-board/pcb/route-r13-1/AegisBioWatch-MainBoard-Route1-r13.kicad_pro
hardware/main-board/pcb/route-r13-1/routing-seed-r13-1.json
```

## Required KiCad validation

After generation:

```bash
cd hardware/main-board/pcb/route-r13-1
kicad-cli pcb drc --format json --severity-all \
  -o /tmp/drc-r13-route1.json AegisBioWatch-MainBoard-Route1-r13.kicad_pcb
```

Record separately:

- rule violations;
- unconnected items.

Do not infer the new unconnected count. The executed KiCad result is packaged by:

```bash
R13_ROUTE1_DRC_JSON=/tmp/drc-r13-route1.json \
python3 tools/package-pcb-r13-route1-evidence.py
```

## Acceptance for the next routing pass

Before expanding routing beyond route-1:

- route-1 rule violations must be 0;
- VOUT1 and VOUT2 must be part of the correct post-inductor output nodes;
- no PMIC component/track may intrude into RF/crystal or Bio sensitive reserves;
- local switching-current geometry must be visually reviewed against Nordic authority;
- SW copper must remain compact;
- local return topology must enter the continuous GND system intentionally;
- any provisional via/track geometry must remain clearly non-release until fab/DFM closure.

Partial routing means `unconnected > 0` is expected. It must be reported as such and must not be described as a complete PCB DRC pass.

## Privacy boundary

This revision contains engineering-only hardware information and no individual health history, private correspondence, medication names/doses, or identifiable health information.
