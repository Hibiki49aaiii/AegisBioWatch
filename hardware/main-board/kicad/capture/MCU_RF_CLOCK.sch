EESchema Schematic File Version 4
LIBS:AegisBioWatch
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "AegisBioWatch MCU / RF / Clock"
Date "2026-08-07"
Rev "Rev.0 / Phase 1 r2"
Comp "AegisBioWatch"
Comment1 "CAPTURE DRAFT - ERC pending"
Comment2 "PCB release prohibited until reference gates close"
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L AegisBioWatch:nRF54L15-QFAA U1
U 1 1 88EA03
P 5200 3900
F 0 "U1" H 5350 4000 50  0000 C CNN
F 1 "nRF54L15-QFAA" H 5450 3800 50  0000 C CNN
F 2 "Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.6x4.6mm" H 5200 3900 50  0001 C CNN
F 3 "https://docs.nordicsemi.com/bundle/ps_nrf54l15" H 5200 3900 50  0001 C CNN
	1    5200 3900
	1 0 0 -1
$EndComp
Text Label 4200 2400 0    35   ~ 0
NRF_XL1
Text Label 4200 2525 0    35   ~ 0
NRF_XL2
Text Label 4200 2650 0    35   ~ 0
GPIO_SPARE0
Text Label 4200 2775 0    35   ~ 0
DISP_PWR_EN
Text Label 4200 2900 0    35   ~ 0
SIDE_BUTTON
Text Label 4200 3025 0    35   ~ 0
PMIC_INT
Text Label 4200 3150 0    35   ~ 0
HAPTIC_EN
Text Label 4200 3275 0    35   ~ 0
BIO_SAFE_EN
Text Label 4200 3400 0    35   ~ 0
GPIO_SPARE_CLK
Text Label 4200 3525 0    35   ~ 0
+1V8
Text Label 4200 3650 0    35   ~ 0
DISP_QSPI_D3
Text Label 4200 3775 0    35   ~ 0
DISP_QSPI_SCK
Text Label 4200 3900 0    35   ~ 0
DISP_QSPI_D0
Text Label 4200 4025 0    35   ~ 0
DISP_QSPI_D2
Text Label 4200 4150 0    35   ~ 0
DISP_QSPI_D1
Text Label 4200 4275 0    35   ~ 0
DISP_QSPI_CS_N
Text Label 4200 4400 0    35   ~ 0
AUX_SPI_SCK
Text Label 4200 4525 0    35   ~ 0
SWO
Text Label 4200 4650 0    35   ~ 0
AUX_SPI_MOSI
Text Label 4200 4775 0    35   ~ 0
AUX_SPI_MISO
Text Label 4200 4900 0    35   ~ 0
FLASH_CS_N
Text Label 4200 5025 0    35   ~ 0
+1V8
Text Label 4200 5150 0    35   ~ 0
SYS_I2C_SDA
Text Label 4200 5275 0    35   ~ 0
SYS_I2C_SCL
Text Label 4200 5400 0    35   ~ 0
SWDIO
Text Label 6200 2400 2    35   ~ 0
SWDCLK
Text Label 6200 2525 2    35   ~ 0
DISP_RST_N
Text Label 6200 2650 2    35   ~ 0
DISP_TE
Text Label 6200 2775 2    35   ~ 0
TOUCH_RST_N
Text Label 6200 2900 2    35   ~ 0
NRF_RESET_N
Text Label 6200 3025 2    35   ~ 0
RF_ANT
Text Label 6200 3150 2    35   ~ 0
GND
Text Label 6200 3275 2    35   ~ 0
NRF_DECRF
Text Label 6200 3400 2    35   ~ 0
NRF_XC1
Text Label 6200 3525 2    35   ~ 0
NRF_XC2
Text Label 6200 3650 2    35   ~ 0
+1V8
Text Label 6200 3775 2    35   ~ 0
TOUCH_INT_N
Text Label 6200 3900 2    35   ~ 0
IMU_INT2
Text Label 6200 4025 2    35   ~ 0
IMU_INT1
Text Label 6200 4150 2    35   ~ 0
PPG_INT_N
Text Label 6200 4275 2    35   ~ 0
EDA_INT_N
Text Label 6200 4400 2    35   ~ 0
BIO_SPI_CS_N
Text Label 6200 4525 2    35   ~ 0
NRF_DECA
Text Label 6200 4650 2    35   ~ 0
GND
Text Label 6200 4775 2    35   ~ 0
NRF_DECD
Text Label 6200 4900 2    35   ~ 0
NRF_DCC
Text Label 6200 5025 2    35   ~ 0
+1V8
Text Label 6200 5150 2    35   ~ 0
+1V8
Text Label 6200 5275 2    35   ~ 0
GND
$Comp
L Device:Crystal_Small Y1
U 1 1 5F9AB0
P 2600 2000
F 0 "Y1" H 2750 2100 50  0000 C CNN
F 1 "32MHz" H 2850 1900 50  0000 C CNN
F 2 "" H 2600 2000 50  0001 C CNN
F 3 "~" H 2600 2000 50  0001 C CNN
	1    2600 2000
	1 0 0 -1
$EndComp
Text Label 2450 2000 2    35   ~ 0
NRF_XC1
Text Label 2750 2000 0    35   ~ 0
NRF_XC2
$Comp
L Device:Crystal_Small Y2
U 1 1 C737FC
P 2600 2500
F 0 "Y2" H 2750 2600 50  0000 C CNN
F 1 "32.768kHz" H 2850 2400 50  0000 C CNN
F 2 "" H 2600 2500 50  0001 C CNN
F 3 "~" H 2600 2500 50  0001 C CNN
	1    2600 2500
	1 0 0 -1
$EndComp
Text Label 2450 2500 2    35   ~ 0
NRF_XL1
Text Label 2750 2500 0    35   ~ 0
NRF_XL2
Text Notes 700 700 0    50   ~ 0
U1 QFN48 pad map captured; display QSPI, AUX SPI, I2C, interrupts, SWD and clocks are real nets.
Text Notes 700 850 0    50   ~ 0
REFERENCE GATE: DECA/DECRF/DECD/DCC and RF harmonic/matching network must be copied exactly from CC0 QFAA reference block.
Text Notes 700 1000 0    50   ~ 0
Do not route PCB or release Gerbers until that gate is closed and ERC is run in KiCad 9.
Text Notes 700 1150 0    50   ~ 0
Reference block: feastorg/KiCad-Master-Lib nRF54L15-QFAA_Reference_Design (CC0 1.0).
$EndSCHEMATC
