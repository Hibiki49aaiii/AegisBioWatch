EESchema Schematic File Version 4
LIBS:AegisBioWatch
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "AegisBioWatch Storage / Haptic"
Date "2026-08-07"
Rev "Rev.0 / Phase 1 r6"
Comp "AegisBioWatch"
Comment1 "CAPTURE DRAFT - ERC pending"
Comment2 "Flash/LRA MPNs selected; footprints/mechanical integration still review-gated"
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L AegisBioWatch:W25Q256JW-SPI U3
U 1 1 8465B4
P 3600 2700
F 0 "U3" H 3750 2800 50  0000 C CNN
F 1 "W25Q256JWPIQ 256Mbit" H 4000 2600 50  0000 C CNN
F 2 "AegisBioWatch:WSON8_6x5_W25Q256JWPIQ_VERIFY" H 3600 2700 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/winbond-electronics/W25Q256JWPIQ/15182111" H 3600 2700 50  0001 C CNN
	1    3600 2700
	1 0 0 -1
$EndComp
Text Label 2700 2250 0    35   ~ 0
FLASH_CS_N
Text Label 2700 2550 0    35   ~ 0
AUX_SPI_MISO
Text Label 2700 2850 0    35   ~ 0
FLASH_WP_N
Text Label 2700 3150 0    35   ~ 0
GND
Text Label 4500 2250 0    35   ~ 0
AUX_SPI_MOSI
Text Label 4500 2550 0    35   ~ 0
AUX_SPI_SCK
Text Label 4500 2850 0    35   ~ 0
FLASH_HOLD_N
Text Label 4500 3150 0    35   ~ 0
+1V8
$Comp
L Device:R_Small R301
U 1 1 C4420D
P 1900 2850
F 0 "R301" H 2050 2950 50  0000 C CNN
F 1 "47k PU" H 2150 2750 50  0000 C CNN
F 2 "" H 1900 2850 50  0001 C CNN
F 3 "~" H 1900 2850 50  0001 C CNN
	1    1900 2850
	1 0 0 -1
$EndComp
Text Label 1900 2550 0    35   ~ 0
+1V8
Text Label 1900 3150 0    35   ~ 0
FLASH_WP_N
$Comp
L Device:R_Small R302
U 1 1 150A52
P 2250 2850
F 0 "R302" H 2400 2950 50  0000 C CNN
F 1 "47k PU" H 2500 2750 50  0000 C CNN
F 2 "" H 2250 2850 50  0001 C CNN
F 3 "~" H 2250 2850 50  0001 C CNN
	1    2250 2850
	1 0 0 -1
$EndComp
Text Label 2250 2550 0    35   ~ 0
+1V8
Text Label 2250 3150 0    35   ~ 0
FLASH_HOLD_N
$Comp
L Device:C_Small C301
U 1 1 2478DB
P 5000 2800
F 0 "C301" H 5150 2900 50  0000 C CNN
F 1 "100nF" H 5250 2700 50  0000 C CNN
F 2 "" H 5000 2800 50  0001 C CNN
F 3 "~" H 5000 2800 50  0001 C CNN
	1    5000 2800
	1 0 0 -1
$EndComp
Text Label 5000 2550 0    35   ~ 0
+1V8
Text Label 5000 3050 0    35   ~ 0
GND
$Comp
L Device:C_Small C302
U 1 1 A64B7C
P 5350 2800
F 0 "C302" H 5500 2900 50  0000 C CNN
F 1 "1uF" H 5600 2700 50  0000 C CNN
F 2 "" H 5350 2800 50  0001 C CNN
F 3 "~" H 5350 2800 50  0001 C CNN
	1    5350 2800
	1 0 0 -1
$EndComp
Text Label 5350 2550 0    35   ~ 0
+1V8
Text Label 5350 3050 0    35   ~ 0
GND
Text Notes 1500 1700 0    45   ~ 0
32MB local logger: W25Q256JWPIQ, 1.7-1.95V, WSON-8 6x5. Standard SPI on AUX bus; landing pattern still DFM-reviewed before PCB release.
$Comp
L AegisBioWatch:DRV2605LDGS U4
U 1 1 23FD2B
P 7400 4700
F 0 "U4" H 7550 4800 50  0000 C CNN
F 1 "DRV2605LDGSR" H 7650 4600 50  0000 C CNN
F 2 "Package_SO:VSSOP-10_3x3mm_P0.5mm" H 7400 4700 50  0001 C CNN
F 3 "https://www.ti.com/lit/ds/symlink/drv2605l.pdf" H 7400 4700 50  0001 C CNN
	1    7400 4700
	1 0 0 -1
$EndComp
Text Label 6500 4100 0    35   ~ 0
HAPTIC_REG
Text Label 6500 4400 0    35   ~ 0
SYS_I2C_SCL
Text Label 6500 4700 0    35   ~ 0
SYS_I2C_SDA
Text Label 6500 5000 0    35   ~ 0
HAPTIC_TRIG
Text Label 6500 5300 0    35   ~ 0
HAPTIC_EN
Text Label 8300 4100 0    35   ~ 0
NC_DRV2605_PIN6
Text Label 8300 4400 0    35   ~ 0
HAPTIC_OUT_P
Text Label 8300 4700 0    35   ~ 0
GND
Text Label 8300 5000 0    35   ~ 0
HAPTIC_OUT_N
Text Label 8300 5300 0    35   ~ 0
VSYS_HAPTIC
$Comp
L Device:C_Small C303
U 1 1 B8CF28
P 6050 4100
F 0 "C303" H 6200 4200 50  0000 C CNN
F 1 "1uF REG / TI VERIFIED" H 6500 4000 50  0000 C CNN
F 2 "" H 6050 4100 50  0001 C CNN
F 3 "~" H 6050 4100 50  0001 C CNN
	1    6050 4100
	1 0 0 -1
$EndComp
Text Label 6050 3850 0    35   ~ 0
HAPTIC_REG
Text Label 6050 4350 0    35   ~ 0
GND
$Comp
L Device:C_Small C304
U 1 1 6781FB
P 8750 5300
F 0 "C304" H 8900 5400 50  0000 C CNN
F 1 "100nF" H 9000 5200 50  0000 C CNN
F 2 "" H 8750 5300 50  0001 C CNN
F 3 "~" H 8750 5300 50  0001 C CNN
	1    8750 5300
	1 0 0 -1
$EndComp
Text Label 8750 5050 0    35   ~ 0
VSYS_HAPTIC
Text Label 8750 5550 0    35   ~ 0
GND
$Comp
L Device:C_Small C305
U 1 1 E68CEF
P 9100 5300
F 0 "C305" H 9250 5400 50  0000 C CNN
F 1 "1uF" H 9350 5200 50  0000 C CNN
F 2 "" H 9100 5300 50  0001 C CNN
F 3 "~" H 9100 5300 50  0001 C CNN
	1    9100 5300
	1 0 0 -1
$EndComp
Text Label 9100 5050 0    35   ~ 0
VSYS_HAPTIC
Text Label 9100 5550 0    35   ~ 0
GND
$Comp
L Device:R_Small R303
U 1 1 2F0F5B
P 5750 5000
F 0 "R303" H 5900 5100 50  0000 C CNN
F 1 "100k PD" H 6000 4900 50  0000 C CNN
F 2 "" H 5750 5000 50  0001 C CNN
F 3 "~" H 5750 5000 50  0001 C CNN
	1    5750 5000
	1 0 0 -1
$EndComp
Text Label 5750 4700 0    35   ~ 0
HAPTIC_TRIG
Text Label 5750 5300 0    35   ~ 0
GND
$Comp
L Device:R_Small R304
U 1 1 DC4575
P 6100 5300
F 0 "R304" H 6250 5400 50  0000 C CNN
F 1 "100k PD" H 6350 5200 50  0000 C CNN
F 2 "" H 6100 5300 50  0001 C CNN
F 3 "~" H 6100 5300 50  0001 C CNN
	1    6100 5300
	1 0 0 -1
$EndComp
Text Label 6100 5000 0    35   ~ 0
HAPTIC_EN
Text Label 6100 5600 0    35   ~ 0
GND
$Comp
L Connector_Generic:Conn_01x02 J4
U 1 1 74B358
P 9550 4650
F 0 "J4" H 9700 4800 50  0000 C CNN
F 1 "C10-100 LRA" H 9800 4600 50  0000 C CNN
F 2 "" H 9550 4700 50  0001 C CNN
F 3 "~" H 9550 4700 50  0001 C CNN
	1    9550 4650
	1 0 0 -1
$EndComp
Text Label 9200 4650 0    35   ~ 0
HAPTIC_OUT_P
Text Label 9200 4750 0    35   ~ 0
HAPTIC_OUT_N
Text Notes 6050 3650 0    43   ~ 0
DRV2605L supply moved to VSYS_HAPTIC. C10-100: 10mm x 3.7mm, 175Hz, 2Vrms rated, 2.05Vrms max, 67mA typ / 90mA max.
Text Notes 6050 3800 0    40   ~ 0
Pin 6 is NC. C(REG)=1uF and C(VDD)=1uF are verified against TI guidance; C304=100nF is additional local HF bypass.
Text Notes 700 700 0    48   ~ 0
r6 STORAGE_HAPTIC: W25Q256JWPIQ and C10-100 selected; haptic rail moved off BUCK2 to VSYS-derived rail.
Text Notes 700 850 0    42   ~ 0
No full-rate logger guarantee yet: firmware duty cycle and raw-buffer policy determine usable retention.
$Comp
L Device:R_Small R305
U 1 1 620305
P 7850 6150
F 0 "R305" V 7750 6150 50  0000 C CNN
F 1 "0R / FB OPTION" V 7950 6150 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" H 7850 6150 50  0001 C CNN
F 3 "~" H 7850 6150 50  0001 C CNN
	1    7850 6150
	0 -1 -1 0
$EndComp
Text Label 7400 6150 2    35   ~ 0
VSYS
Text Label 8300 6150 0    35   ~ 0
VSYS_HAPTIC
Wire Wire Line
	7400 6150 7750 6150
Wire Wire Line
	7950 6150 8300 6150
Text Notes 7000 6450 0    40   ~ 0
R305 starts as 0R. Replace by ferrite only if EMI measurements justify it; do not add DC resistance casually.
Text Notes 700 7350 0    36   ~ 0
WIRE_AUDIT_R6_BEGIN
Wire Wire Line
	1900 2550 1900 2750
Wire Wire Line
	1900 2950 1900 3150
Wire Wire Line
	2250 2550 2250 2750
Wire Wire Line
	2250 2950 2250 3150
Wire Wire Line
	5000 2550 5000 2700
Wire Wire Line
	5000 2900 5000 3050
Wire Wire Line
	5350 2550 5350 2700
Wire Wire Line
	5350 2900 5350 3050
Wire Wire Line
	6050 3850 6050 4000
Wire Wire Line
	6050 4200 6050 4350
Wire Wire Line
	8750 5050 8750 5200
Wire Wire Line
	8750 5400 8750 5550
Wire Wire Line
	9100 5050 9100 5200
Wire Wire Line
	9100 5400 9100 5550
Wire Wire Line
	5750 4700 5750 4900
Wire Wire Line
	5750 5100 5750 5300
Wire Wire Line
	6100 5000 6100 5200
Wire Wire Line
	6100 5400 6100 5600
Wire Wire Line
	9200 4650 9350 4650
Wire Wire Line
	9200 4750 9350 4750
Text Notes 700 7500 0    36   ~ 0
WIRE_AUDIT_R6_END
$EndSCHEMATC
