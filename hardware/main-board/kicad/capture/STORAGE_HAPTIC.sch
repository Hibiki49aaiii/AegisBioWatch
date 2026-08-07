EESchema Schematic File Version 4
LIBS:AegisBioWatch
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "AegisBioWatch Storage / Haptic"
Date "2026-08-07"
Rev "Rev.0 / Phase 1 r4"
Comp "AegisBioWatch"
Comment1 "CAPTURE DRAFT - ERC pending"
Comment2 "Flash package and LRA part still provisional"
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L AegisBioWatch:W25Q512NW-SPI U3
U 1 1 8465B4
P 3600 2700
F 0 "U3" H 3750 2800 50  0000 C CNN
F 1 "W25Q512NW 512Mbit" H 3850 2600 50  0000 C CNN
F 2 "" H 3600 2700 50  0001 C CNN
F 3 "https://www.winbond.com/hq/product/code-storage-flash/qspi-nor/w25q-nw/" H 3600 2700 50  0001 C CNN
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
64MB local logger: standard SPI on AUX bus; WP#/HOLD# pulled high. Exact package/MPN remains PROVISIONAL.
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
+3V0
$Comp
L Device:C_Small C303
U 1 1 B8CF28
P 6050 4100
F 0 "C303" H 6200 4200 50  0000 C CNN
F 1 "1uF VERIFY_TI" H 6300 4000 50  0000 C CNN
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
+3V0
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
+3V0
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
F 1 "LRA_ACTUATOR" H 9800 4600 50  0000 C CNN
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
DRV2605L supply = +3V0. LRA peak-current budget must be validated against selected actuator and nPM1300 rail.
Text Notes 6050 3800 0    40   ~ 0
Pin 6 is treated as NC for DRV2605L; REG capacitor value is flagged for TI-datasheet review before manufacture.
Text Notes 700 700 0    48   ~ 0
r4 STORAGE_HAPTIC: real SPI/I2C/enable/output nets captured; package/actuator selection remains gated.
Text Notes 700 850 0    42   ~ 0
No full-rate logger guarantee yet: firmware duty cycle and raw-buffer policy determine usable retention.
Text Notes 700 7350 0    36   ~ 0
WIRE_AUDIT_R4_BEGIN
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
WIRE_AUDIT_R4_END
$EndSCHEMATC
