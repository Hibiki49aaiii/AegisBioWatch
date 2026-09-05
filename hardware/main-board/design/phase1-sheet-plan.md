# Phase 1 schematic sheet plan

## Sheet 1 — SYSTEM
- project title/revision
- global power rails: `VBAT`, `VSYS`, `+1V8`, `+3V0`, `DISP_SW`, `BIO_SW`
- global buses: `SYS_I2C_*`, `AUX_SPI_*`, `DISP_QSPI_*`
- hierarchical connections to all sheets
- test points and external connectors overview

## Sheet 2 — MCU_RF_CLOCK
- nRF54L15-QFAA QFN48
- all VDD pins on +1V8
- VSS/VSS_PA/exposed pad grounding
- DCC + 4.7 uH network
- DECA/DECRF/DECD decoupling exactly from Nordic configuration 1
- 32 MHz crystal
- 32.768 kHz crystal
- antenna matching/harmonic filter exactly from Nordic QFAA v0.8 reference
- 50-ohm RF launch to antenna matching/antenna
- no NFC in Rev.0

**PCB note:** C6 grounding must follow Nordic's QFAA reference layout note; do not
simply drop it into the ground plane away from pin 32/VSS die pad.

## Sheet 3 — PMIC_CHARGER
- nPM1300 QFN32
- Nordic Configuration 1
- BUCK1 = +1V8 via 47k VSET1
- BUCK2 = +3V0 via 150k VSET2
- 2.2 uH inductors
- battery NTC
- magnetic 5 V charger input protection
- VSYS / VBAT measurement test points
- ship-mode hold/wake
- TWI connection to MCU
- charge-present/event GPIO to MCU

Magnetic dock is **not USB-C**, therefore CC1/CC2 are not wired as a fabricated
Type-C source/sink interface.

## Sheet 4 — DISPLAY_TOUCH
- 1.75" 390x450 CO5300-class AMOLED placeholder connector
- dedicated `DISP_QSPI_SCK/D0/D1/D2/D3/CS_N`
- reset, TE/status, power-enable reservations
- CST820B-class touch on `SYS_I2C`
- touch interrupt + reset
- panel power rails remain parameterized until supplier FPC is frozen

## Sheet 5 — STORAGE_HAPTIC
- W25Q512NW 1.8 V class Flash on `AUX_SPI`
- `FLASH_CS_N`
- 1.8 V decoupling
- DRV2605L on `SYS_I2C`
- LRA connector
- optional haptic enable
- keep haptic current loops away from PPG/Bio board interconnect

## Sheet 6 — BIO_INTERFACE
- main↔bio board connector
- +1V8, +3V0/BIO_SW, GND
- `SYS_I2C_SDA/SCL`
- `AUX_SPI_SCK/MOSI/MISO`
- `BIO_SPI_CS_N`
- `PPG_INT_N`
- `EDA_INT_N`
- `IMU_INT1/2`
- `BIO_SAFE_EN`
- charge-present / safety signal
- at least 2 spare GPIOs if connector pin count permits

## Sheet 7 — DEBUG_TEST
- SWDIO / SWDCLK / nRESET / GND / +1V8 sense
- SWO optional pad
- UART pads optional
- VBUS/VBAT/VSYS/+1V8/+3V0 current/voltage test points
- production pogo footprint
