# nPM1300 errata gate — r5

The PCB footprint remains nPM1300 QFN32, but the **procured build code must be
recorded before firmware/power sequencing freeze**.

For Revision 1 build codes `QEAA-C00` / `CAAA-C00`, Nordic documents anomalies
including:
- charger recovery with some battery protection modules after over-discharge;
- LDO input-voltage droop during startup;
- reset risk when an LDO is started from VSYS near the power-fail threshold.

Design consequences:
- do not hard-code an aggressive charge profile before the exact cell/PCM is known;
- do not enable both LDOs simultaneously during startup;
- if LDO input is VSYS while powered by VBUS, establish an appropriate VBUS current limit before enabling LDO loads;
- keep sufficient VSYS/POF margin when battery-powered;
- record the actual PMIC marking/build code in manufacturing records.

Firmware applies only the workarounds that correspond to the purchased device
revision/build and selected battery.
