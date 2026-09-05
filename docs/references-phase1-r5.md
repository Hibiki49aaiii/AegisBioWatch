# Phase 1 r5 reference authority

Use vendor-current documentation as the electrical/layout authority.

## Nordic nPM1300

- Product Specification / reference circuitry:
  https://docs.nordicsemi.com/r/bundle/ps_npm1300/page/chapters/hw_layout/ref_circuitry/frontpage.html
- Pin assignments:
  https://docs.nordicsemi.com/r/bundle/ps_npm1300/page/pin.html
- Hardware Design Guidelines:
  https://docs.nordicsemi.com/r/bundle/nwp_050/
- Revision 1 errata:
  https://docs.nordicsemi.com/r/bundle/errata_npm1300_rev1/

The current QFN Config.1 schematic is the authority for the PVSS1/PVSS2 local
net-tie intent. The hardware-design guideline is the authority for keeping the
underlying ground plane continuous and minimizing switching-current loop area.

## Nordic nRF54L15

- Product Specification:
  https://docs.nordicsemi.com/bundle/ps_nrf54l15
- Reference layout:
  https://www.nordicsemi.com/Products/nRF54L15/Reference-layout

## Release policy

Third-party KiCad blocks may be used for independent cross-checking, but vendor
documentation supersedes them when values or topology differ.
