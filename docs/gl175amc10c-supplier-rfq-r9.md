# GL175AMC10C engineering data request — AegisBioWatch

Subject: Engineering datasheet / 24-pin definition request for GL175AMC10C

Hello,

We are evaluating the GL175AMC10C 1.75-inch 390x450 QSPI AMOLED module for a custom wearable device and need the controlled engineering package before PCB layout freeze.

Please provide the latest revision of the following documents/data for the exact **GL175AMC10C / CO5300AF-41 / CST820B** configuration:

1. Full module datasheet and drawing revision.
2. Complete 24-pin connector/FPC pin definition.
3. Pin-1 location and mating/contact orientation.
4. Exact mating connector manufacturer and full part number for `OK-118RM024-35`, including recommended PCB land pattern.
5. Display rail names and min/typ/max voltages.
6. Display typical, maximum and startup/inrush current for representative brightness levels.
7. QSPI/TE/RESET logic-voltage requirements and absolute maximum ratings.
8. Required power-on and power-off rail sequence and timing.
9. CO5300AF-41 initialization command table for this exact panel revision.
10. Maximum QSPI clock and setup/hold timing.
11. CST820B supply voltage and I/O voltage.
12. CST820B I2C address(es), reset timing, interrupt polarity/mode and required pull-ups.
13. Required external capacitors/resistors/ESD protection not integrated on the module.
14. Sleep/AOD current and wake timing.
15. Mechanical FPC drawing including bend zone, stiffener thickness, keep-out and minimum bend radius.
16. Cover-glass/touch-stack drawing and tolerance.
17. Recommended ESD handling level and module qualification data.
18. Sample/demo initialization code if available.

Please also confirm whether the display and CST820B touch signals are all carried through the same 24-pin connector, and whether the published connector `OK-118RM024-35` is the module-side male connector or the required PCB-side mating part.

We will not freeze the PCB interface until the exact pin definition and power sequencing are confirmed.

Project: AegisBioWatch Rev.0
Application: battery-powered wearable
Interface target: QSPI display + I2C touch

Thank you.
