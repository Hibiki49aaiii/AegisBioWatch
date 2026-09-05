# KiCad — Main Board Rev.0

Status: **schematic-capture-ready / not manufacturing-ready**

Phase 1 electrical architecture is defined in `../design/`.

The next capture sequence is:

1. `MCU_RF_CLOCK`
2. `PMIC_CHARGER`
3. `DISPLAY_TOUCH`
4. `STORAGE_HAPTIC`
5. `BIO_INTERFACE`
6. `DEBUG_TEST`
7. top-level `SYSTEM`

Do not release Gerbers or order assembled PCBs until:

- the schematic has been captured in KiCad;
- ERC is clean or exceptions are documented;
- the actual AMOLED FPC/datasheet is supplier-locked;
- the battery and NTC are selected;
- the Bio Board connector is frozen;
- RF layout is reviewed against Nordic QFAA reference layout.
