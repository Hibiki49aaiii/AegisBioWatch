# nPM1300 functional passive mapping — r5

Authority: current Nordic nPM1300 Product Specification and Hardware Design Guidelines.

AegisBioWatch uses project-local designators.

| Aegis ref | Function | Value |
|---|---|---|
| C101 | VBUS input decoupling | 1.0 µF |
| C102 | VSYS bulk | 10 µF |
| C103 | BUCK1 local input / PVDD-to-PVSS1 return | 10 µF |
| C104 | BUCK2 local input / PVDD-to-PVSS2 return | 10 µF |
| C105 | VBUSOUT mandatory decoupling | 1.0 µF |
| C106 | VBAT decoupling | 2.2 µF |
| C107 | BUCK1 output | 10 µF |
| C108 | BUCK2 output | 10 µF |
| C109, C110 | LOADSW/LDO1 output stability | 10 µF each |
| C111, C112 | LOADSW/LDO2 output stability | 10 µF each |
| C113 | VDDIO local bypass | 100 nF |
| C114 | RF-sensitive application HF bypass on VSYS/PVDD | 100 nF |
| L101, L102 | BUCK inductors | 2.2 µH, DCR < 400 mΩ |
| R101 | VSET1 | 47 kΩ, 1% → 1.8 V startup |
| R102 | VSET2 | 150 kΩ, 1% → 3.0 V startup |
| R103, R104 | optional TWI pull-ups | 10 kΩ DNP/TUNE |
| NT101, NT102 | local buck return joins | schematic net ties into the same continuous L2 GND plane; physical copper/vias layout-specific |
| R105, R106 | optional VINLDO feeds | 0 Ω option from VSYS |

## Vendor constraints captured

- VOUT1/VOUT2 effective output capacitance must remain within the vendor range.
- VBUSOUT requires a decoupling capacitor even if the function is unused.
- LDO mode requires two nominal 10 µF capacitors per output.
- For RF-sensitive products Nordic recommends an additional 10 nF–100 nF high-frequency capacitor at the buck input/VSYS region.
- The LDO input may be supplied from VOUT1, VOUT2, or VSYS if VIN requirements are satisfied.
- The current QFN Configuration 1 reference schematic explicitly shows PVSS1/PVSS2 net ties into the GND layer; AegisBioWatch preserves that local return intent without splitting the main ground plane.
- nPM1300 Revision 1 errata must be checked against the actual procured build code.

## Still not frozen

- exact MLCC MPNs after DC-bias/effective-capacitance review;
- exact inductor MPNs;
- battery/NTC;
- charge-current policy;
- dock ESD and reverse-polarity parts;
- LS/LDO mode and final rail ownership;
- exact nPM1300 build code / errata applicability.
