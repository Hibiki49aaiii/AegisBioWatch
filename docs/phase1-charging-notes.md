# Rev.0 charging-input notes

## Magnetic 5 V dock with nPM1300

Rev.0 uses a dedicated magnetic 5 V charging dock rather than a USB Type-C receptacle on the watch.

Per the current nPM1300 product specification, if USB Type-C configuration is not used, `CC1` and `CC2` may be left floating or connected to ground. In that condition the VBUS input-current limit remains at the default **100 mA** until host firmware configures a higher limit.

Therefore:

- do not fake a USB Type-C CC negotiation network on the magnetic dock;
- design initial boot/charge behavior so the system is safe at the 100 mA default limit;
- after the MCU/PMIC control path is operational, firmware may configure an appropriate higher VBUS current limit for the dedicated dock;
- the configured limit must remain compatible with the dock supply, PCB thermal design, battery charge-current setting, and the selected cell;
- `CC1`/`CC2` implementation choice (floating vs grounded/testable pads) is reviewed again at schematic freeze;
- charge-current and VBUS-current limits are separate controls and both must be configured deliberately.

Reference: Nordic nPM1300 `SYSREG — System regulator`, VBUS input current limiter / USB port detection.
