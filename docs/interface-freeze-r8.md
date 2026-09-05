# Phase 1 r8 — physical interface freeze

## Closed in r8

### J8 — SWD
- Target: Tag-Connect TC2030 no-legs 6-pin footprint.
- Footprint: `Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical`.
- Pin map: 1 VTRef(+1V8), 2 SWDIO, 3 nRESET, 4 SWCLK, 5 GND, 6 SWO.
- The prior 8-pin debug placeholder is removed. `DISP_PWR_EN` and `GPIO_SPARE_CLK` are no longer exposed on the debug target.

### J9 — side button
- Panasonic `EVQPUK02K`, side-operated SMD.
- Footprint: `Button_Switch_SMD:Panasonic_EVQPUK_EVQPUB`.
- Enclosure-level ingress sealing remains a mechanical requirement; the selected switch is not being used to claim the complete watch is waterproof.

### J101 — ship/wake button
- Panasonic `EVQPLDA15`, top-push SMD.
- Footprint: `Button_Switch_SMD:SW_SPST_Panasonic_EVQPL_3PL_5PL_PT_A15`.
- This is a separate service/wake control; it is not electrically tied to the MCU side-button net.

### J4 — LRA
- Precision Microdrives `C10-100`.
- 100 mm AWG32 leads are direct-soldered to the PCB.
- Footprint: `Connector_Wire:SolderWire-0.127sqmm_1x02_P3.7mm_D0.48mm_OD1mm_Relief`.
- Add enclosure strain relief; do not allow the solder joints to carry repeated mechanical load.

## Still open
- J3 magnetic dock pad geometry/spacing.
- J5 AMOLED physical 24-pin FPC.
- J6 touch physical interface / voltage-level decision.
