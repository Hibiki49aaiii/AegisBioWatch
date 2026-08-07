EESchema Schematic File Version 4
LIBS:AegisBioWatch
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "AegisBioWatch MCU / RF / Clock"
Date "2026-08-07"
Rev "Rev.0 / Phase 1 r4"
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
NRF_RESET_RAW
Text Label 6200 3025 2    35   ~ 0
RF_MCU
Text Label 6200 3150 2    35   ~ 0
GND
Text Label 6200 3275 2    35   ~ 0
NRF_DECA_RF
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
NRF_DECA_RF
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
$Comp
L Device:C_Small C1
U 1 1 797CB7
P 7300 1800
F 0 "C1" H 7450 1900 50  0000 C CNN
F 1 "10uF" H 7550 1700 50  0000 C CNN
F 2 "" H 7300 1800 50  0001 C CNN
F 3 "~" H 7300 1800 50  0001 C CNN
	1    7300 1800
	1 0 0 -1
$EndComp
Text Label 7300 1550 0    35   ~ 0
+1V8
Text Label 7300 2050 0    35   ~ 0
GND
$Comp
L Device:C_Small C2
U 1 1 B581E6
P 7700 1800
F 0 "C2" H 7850 1900 50  0000 C CNN
F 1 "100nF" H 7950 1700 50  0000 C CNN
F 2 "" H 7700 1800 50  0001 C CNN
F 3 "~" H 7700 1800 50  0001 C CNN
	1    7700 1800
	1 0 0 -1
$EndComp
Text Label 7700 1550 0    35   ~ 0
+1V8
Text Label 7700 2050 0    35   ~ 0
GND
$Comp
L Device:C_Small C3
U 1 1 3DDA1F
P 8100 1800
F 0 "C3" H 8250 1900 50  0000 C CNN
F 1 "100nF" H 8350 1700 50  0000 C CNN
F 2 "" H 8100 1800 50  0001 C CNN
F 3 "~" H 8100 1800 50  0001 C CNN
	1    8100 1800
	1 0 0 -1
$EndComp
Text Label 8100 1550 0    35   ~ 0
+1V8
Text Label 8100 2050 0    35   ~ 0
GND
$Comp
L Device:C_Small C4
U 1 1 AC8758
P 8500 1800
F 0 "C4" H 8650 1900 50  0000 C CNN
F 1 "100nF" H 8750 1700 50  0000 C CNN
F 2 "" H 8500 1800 50  0001 C CNN
F 3 "~" H 8500 1800 50  0001 C CNN
	1    8500 1800
	1 0 0 -1
$EndComp
Text Label 8500 1550 0    35   ~ 0
+1V8
Text Label 8500 2050 0    35   ~ 0
GND
$Comp
L Device:C_Small C5
U 1 1 78191F
P 8900 1800
F 0 "C5" H 9050 1900 50  0000 C CNN
F 1 "100nF" H 9150 1700 50  0000 C CNN
F 2 "" H 8900 1800 50  0001 C CNN
F 3 "~" H 8900 1800 50  0001 C CNN
	1    8900 1800
	1 0 0 -1
$EndComp
Text Label 8900 1550 0    35   ~ 0
+1V8
Text Label 8900 2050 0    35   ~ 0
GND
Text Notes 7150 1300 0    45   ~ 0
VDD decoupling — QFN48 reference-block cross-check complete
$Comp
L Device:L_Small L2
U 1 1 3FE3DD
P 7000 3200
F 0 "L2" H 7150 3300 50  0000 C CNN
F 1 "2.7nH" H 7250 3100 50  0000 C CNN
F 2 "" H 7000 3200 50  0001 C CNN
F 3 "~" H 7000 3200 50  0001 C CNN
	1    7000 3200
	0 -1 -1 0
$EndComp
Text Label 6550 3200 0    35   ~ 0
RF_MCU
Text Label 7450 3200 0    35   ~ 0
RF_A
$Comp
L Device:C_Small C10
U 1 1 C805D3
P 7450 3650
F 0 "C10" H 7600 3750 50  0000 C CNN
F 1 "1.5pF" H 7700 3550 50  0000 C CNN
F 2 "" H 7450 3650 50  0001 C CNN
F 3 "~" H 7450 3650 50  0001 C CNN
	1    7450 3650
	1 0 0 -1
$EndComp
Text Label 7450 3400 0    35   ~ 0
RF_A
Text Label 7450 3900 0    35   ~ 0
GND
$Comp
L Device:L_Small L3
U 1 1 D11522
P 8000 3200
F 0 "L3" H 8150 3300 50  0000 C CNN
F 1 "3.5nH" H 8250 3100 50  0000 C CNN
F 2 "" H 8000 3200 50  0001 C CNN
F 3 "~" H 8000 3200 50  0001 C CNN
	1    8000 3200
	0 -1 -1 0
$EndComp
Text Label 7550 3200 0    35   ~ 0
RF_A
Text Label 8450 3200 0    35   ~ 0
RF_B
$Comp
L Device:C_Small C11
U 1 1 9563D9
P 8450 3650
F 0 "C11" H 8600 3750 50  0000 C CNN
F 1 "2.0pF" H 8700 3550 50  0000 C CNN
F 2 "" H 8450 3650 50  0001 C CNN
F 3 "~" H 8450 3650 50  0001 C CNN
	1    8450 3650
	1 0 0 -1
$EndComp
Text Label 8450 3400 0    35   ~ 0
RF_B
Text Label 8450 3900 0    35   ~ 0
GND
$Comp
L Device:L_Small L4
U 1 1 E19BF1
P 9000 3200
F 0 "L4" H 9150 3300 50  0000 C CNN
F 1 "3.5nH" H 9250 3100 50  0000 C CNN
F 2 "" H 9000 3200 50  0001 C CNN
F 3 "~" H 9000 3200 50  0001 C CNN
	1    9000 3200
	0 -1 -1 0
$EndComp
Text Label 8550 3200 0    35   ~ 0
RF_B
Text Label 9450 3200 0    35   ~ 0
RF_ANT
$Comp
L Device:C_Small C12
U 1 1 A46B13
P 9450 3650
F 0 "C12" H 9600 3750 50  0000 C CNN
F 1 "0.3pF" H 9700 3550 50  0000 C CNN
F 2 "" H 9450 3650 50  0001 C CNN
F 3 "~" H 9450 3650 50  0001 C CNN
	1    9450 3650
	1 0 0 -1
$EndComp
Text Label 9450 3400 0    35   ~ 0
RF_ANT
Text Label 9450 3900 0    35   ~ 0
GND
Text Notes 6750 2850 0    42   ~ 0
RF_MCU → 2.7nH → [1.5pF↓] → 3.5nH → [2.0pF↓] → 3.5nH → [0.3pF↓] → RF_ANT
Text Notes 6750 3000 0    42   ~ 0
Values/topology independently match two nRF54L15 QFN48 KiCad reference blocks; layout must still follow Nordic placement.
$Comp
L Device:R_Small R1
U 1 1 1EC394
P 7600 4650
F 0 "R1" H 7750 4750 50  0000 C CNN
F 1 "1k" H 7850 4550 50  0000 C CNN
F 2 "" H 7600 4650 50  0001 C CNN
F 3 "~" H 7600 4650 50  0001 C CNN
	1    7600 4650
	0 -1 -1 0
$EndComp
Text Label 7150 4650 0    35   ~ 0
NRF_RESET_RAW
Text Label 8050 4650 0    35   ~ 0
NRF_RESET_N
$Comp
L Device:C_Small C13
U 1 1 94629C
P 7150 5050
F 0 "C13" H 7300 5150 50  0000 C CNN
F 1 "3.9pF" H 7400 4950 50  0000 C CNN
F 2 "" H 7150 5050 50  0001 C CNN
F 3 "~" H 7150 5050 50  0001 C CNN
	1    7150 5050
	1 0 0 -1
$EndComp
Text Label 7150 4800 0    35   ~ 0
NRF_RESET_RAW
Text Label 7150 5300 0    35   ~ 0
GND
Text Notes 6800 4400 0    42   ~ 0
Reset reference: MCU-side 3.9pF to GND + 1k series to external NRF_RESET_N.
Text Notes 6650 5650 0    48   ~ 0
INTERNAL REGULATOR — current Nordic QFN48 Config.1 topology captured
Text Notes 6650 5800 0    40   ~ 0
DECA(pin43) + DECRF(pin33) share NRF_DECA_RF; FB1=120R@100MHz bridges NRF_DECA_RF to NRF_DECD.
Text Notes 6650 5950 0    40   ~ 0
DCC(pin46) -> L1=4.7uH -> DECD(pin45); DECD has 2.2uF to GND.
Text Notes 6650 6100 0    40   ~ 0
NRF_DECA_RF has 2.2uF + 10nF + 2.2nF to GND. Values follow current Nordic Config.1 BOM.
$Comp
L Device:FerriteBead_Small FB1
U 1 1 7FD96D
P 7200 6500
F 0 "FB1" H 7350 6600 50  0000 C CNN
F 1 "120R@100MHz" H 7500 6400 50  0000 C CNN
F 2 "" H 7200 6500 50  0001 C CNN
F 3 "~" H 7200 6500 50  0001 C CNN
	1    7200 6500
	1 0 0 -1
$EndComp
Text Label 7200 6250 0    35   ~ 0
NRF_DECA_RF
Text Label 7200 6750 0    35   ~ 0
NRF_DECD
$Comp
L Device:C_Small C7
U 1 1 D811C9
P 7850 6500
F 0 "C7" H 8000 6600 50  0000 C CNN
F 1 "2.2uF" H 8100 6400 50  0000 C CNN
F 2 "" H 7850 6500 50  0001 C CNN
F 3 "~" H 7850 6500 50  0001 C CNN
	1    7850 6500
	1 0 0 -1
$EndComp
Text Label 7850 6250 0    35   ~ 0
NRF_DECA_RF
Text Label 7850 6750 0    35   ~ 0
GND
$Comp
L Device:C_Small C8
U 1 1 A1F8D4
P 8300 6500
F 0 "C8" H 8450 6600 50  0000 C CNN
F 1 "10nF" H 8550 6400 50  0000 C CNN
F 2 "" H 8300 6500 50  0001 C CNN
F 3 "~" H 8300 6500 50  0001 C CNN
	1    8300 6500
	1 0 0 -1
$EndComp
Text Label 8300 6250 0    35   ~ 0
NRF_DECA_RF
Text Label 8300 6750 0    35   ~ 0
GND
$Comp
L Device:C_Small C9
U 1 1 5BC799
P 8750 6500
F 0 "C9" H 8900 6600 50  0000 C CNN
F 1 "2.2nF" H 9000 6400 50  0000 C CNN
F 2 "" H 8750 6500 50  0001 C CNN
F 3 "~" H 8750 6500 50  0001 C CNN
	1    8750 6500
	1 0 0 -1
$EndComp
Text Label 8750 6250 0    35   ~ 0
NRF_DECA_RF
Text Label 8750 6750 0    35   ~ 0
GND
$Comp
L Device:C_Small C6
U 1 1 466D88
P 9250 6500
F 0 "C6" H 9400 6600 50  0000 C CNN
F 1 "2.2uF" H 9500 6400 50  0000 C CNN
F 2 "" H 9250 6500 50  0001 C CNN
F 3 "~" H 9250 6500 50  0001 C CNN
	1    9250 6500
	1 0 0 -1
$EndComp
Text Label 9250 6250 0    35   ~ 0
NRF_DECD
Text Label 9250 6750 0    35   ~ 0
GND
$Comp
L Device:L_Small L1
U 1 1 492E22
P 9800 6500
F 0 "L1" H 9950 6600 50  0000 C CNN
F 1 "4.7uH" H 10050 6400 50  0000 C CNN
F 2 "" H 9800 6500 50  0001 C CNN
F 3 "~" H 9800 6500 50  0001 C CNN
	1    9800 6500
	1 0 0 -1
$EndComp
Text Label 9800 6250 0    35   ~ 0
NRF_DECD
Text Label 9800 6750 0    35   ~ 0
NRF_DCC
Text Notes 6650 7000 0    38   ~ 0
REFERENCE LOCK: values/topology verified against current Nordic QFN48 Config.1 and current nRF54L15-DK supply network.
Text Notes 700 700 0    50   ~ 0
r4: RF/reset/VDD + DECA/DECRF/DECD/DCC network captured; QFN48 pin map/buses/clocks retained.
Text Notes 700 850 0    45   ~ 0
CLOSED GATE: internal-regulator topology/value cross-check completed against current Nordic Config.1.
Text Notes 700 1000 0    45   ~ 0
Do not release Gerbers until native KiCad conversion, ERC, antenna/stackup, enclosure RF and interface freeze are complete.
Text Notes 700 1150 0    42   ~ 0
Reference cross-check: feastorg/KiCad-Master-Lib (CC0) + hlord2000/nordic-lib-kicad (CERN-OHL-P).
Text Notes 700 7350 0    36   ~ 0
WIRE_AUDIT_R4_BEGIN
Wire Wire Line
	2450 2000 2500 2000
Wire Wire Line
	2700 2000 2750 2000
Wire Wire Line
	2450 2500 2500 2500
Wire Wire Line
	2700 2500 2750 2500
Wire Wire Line
	7300 1550 7300 1700
Wire Wire Line
	7300 1900 7300 2050
Wire Wire Line
	7700 1550 7700 1700
Wire Wire Line
	7700 1900 7700 2050
Wire Wire Line
	8100 1550 8100 1700
Wire Wire Line
	8100 1900 8100 2050
Wire Wire Line
	8500 1550 8500 1700
Wire Wire Line
	8500 1900 8500 2050
Wire Wire Line
	8900 1550 8900 1700
Wire Wire Line
	8900 1900 8900 2050
Wire Wire Line
	6550 3200 6900 3200
Wire Wire Line
	7100 3200 7450 3200
Wire Wire Line
	7550 3200 7900 3200
Wire Wire Line
	8100 3200 8450 3200
Wire Wire Line
	8550 3200 8900 3200
Wire Wire Line
	9100 3200 9450 3200
Wire Wire Line
	7450 3400 7450 3550
Wire Wire Line
	7450 3750 7450 3900
Wire Wire Line
	8450 3400 8450 3550
Wire Wire Line
	8450 3750 8450 3900
Wire Wire Line
	9450 3400 9450 3550
Wire Wire Line
	9450 3750 9450 3900
Wire Wire Line
	7150 4650 7500 4650
Wire Wire Line
	7700 4650 8050 4650
Wire Wire Line
	7150 4800 7150 4950
Wire Wire Line
	7150 5150 7150 5300
Wire Wire Line
	7200 6250 7200 6400
Wire Wire Line
	7200 6600 7200 6750
Wire Wire Line
	7850 6250 7850 6400
Wire Wire Line
	7850 6600 7850 6750
Wire Wire Line
	8300 6250 8300 6400
Wire Wire Line
	8300 6600 8300 6750
Wire Wire Line
	8750 6250 8750 6400
Wire Wire Line
	8750 6600 8750 6750
Wire Wire Line
	9250 6250 9250 6400
Wire Wire Line
	9250 6600 9250 6750
Wire Wire Line
	9800 6250 9800 6400
Wire Wire Line
	9800 6600 9800 6750
Text Notes 700 7500 0    36   ~ 0
WIRE_AUDIT_R4_END
$EndSCHEMATC
