# Bus allocation

## Display QSPI — dedicated
| Signal | nRF54L15 |
|---|---|
| D3 | P2.00 |
| SCK | P2.01 |
| D0 | P2.02 |
| D2 | P2.03 |
| D1 | P2.04 |
| CS# | P2.05 |

Reason: reserve the fixed/high-performance QSPI pin group for the AMOLED.

## AUX SPI
| Signal | nRF54L15 |
|---|---|
| SCK | P2.06 |
| MOSI | P2.08 |
| MISO | P2.09 |
| Flash CS# | P2.10 |
| AD5940 CS# | P1.14 |

Flash uses standard SPI in Rev.0. 512 Mbit capacity is retained, but QPI is not
required because display bandwidth has priority.

## Shared I2C/TWI
| Signal | nRF54L15 |
|---|---|
| SDA | P0.00 |
| SCL | P0.01 |

Expected devices:
- nPM1300
- touch controller
- DRV2605L
- digital sensors exposed by Bio Board

Use one pull-up pair on Main Board initially, with DNM/alternate-value options.
Final value is determined after total bus capacitance and target speed are known.
