EESchema Schematic File Version 4
LIBS:AegisBioWatch
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "AegisBioWatch Display / Touch"
Date "2026-08-07"
Rev "Rev.0 / Phase 1 r4"
Comp "AegisBioWatch"
Comment1 "LOGICAL CAPTURE - final supplier FPC pinout not frozen"
Comment2 "Touch I/O voltage compatibility remains a release gate"
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector_Generic:Conn_01x10 J5
U 1 1 410001
P 3300 2950
F 0 "J5" H 3450 3100 50  0000 C CNN
F 1 "AMOLED_LOGIC_PLACEHOLDER" H 3900 2900 50  0000 C CNN
F 2 "" H 3300 3000 50  0001 C CNN
F 3 "~" H 3300 3000 50  0001 C CNN
	1    3300 2950
	1 0 0 -1
$EndComp
Text Label 2950 2550 0    35   ~ 0
DISP_SW
Text Label 2950 2650 0    35   ~ 0
GND
Text Label 2950 2750 0    35   ~ 0
DISP_QSPI_SCK
Text Label 2950 2850 0    35   ~ 0
DISP_QSPI_D0
Text Label 2950 2950 0    35   ~ 0
DISP_QSPI_D1
Text Label 2950 3050 0    35   ~ 0
DISP_QSPI_D2
Text Label 2950 3150 0    35   ~ 0
DISP_QSPI_D3
Text Label 2950 3250 0    35   ~ 0
DISP_QSPI_CS_N
Text Label 2950 3350 0    35   ~ 0
DISP_RST_N
Text Label 2950 3450 0    35   ~ 0
DISP_TE
Text Notes 1700 2100 0    45   ~ 0
J5 is a LOGICAL placeholder only. It is not the production AMOLED FPC pin order or footprint.
Text Notes 1700 2250 0    42   ~ 0
DISP_SW voltage/current and panel initialization sequence remain supplier-datasheet gates.
$Comp
L Connector_Generic:Conn_01x06 J6
U 1 1 410002
P 3300 4950
F 0 "J6" H 3450 5100 50  0000 C CNN
F 1 "TOUCH_LOGIC_PLACEHOLDER" H 3900 4900 50  0000 C CNN
F 2 "" H 3300 5000 50  0001 C CNN
F 3 "~" H 3300 5000 50  0001 C CNN
	1    3300 4950
	1 0 0 -1
$EndComp
Text Label 2950 4750 0    35   ~ 0
TOUCH_VDD
Text Label 2950 4850 0    35   ~ 0
GND
Text Label 2950 4950 0    35   ~ 0
TOUCH_SDA
Text Label 2950 5050 0    35   ~ 0
TOUCH_SCL
Text Label 2950 5150 0    35   ~ 0
TOUCH_RST_N
Text Label 2950 5250 0    35   ~ 0
TOUCH_INT_N
$Comp
L Device:R_Small R401
U 1 1 410003
P 5600 4650
F 0 "R401" H 5750 4750 50  0000 C CNN
F 1 "0R LINK" H 5850 4550 50  0000 C CNN
F 2 "" H 5600 4650 50  0001 C CNN
F 3 "~" H 5600 4650 50  0001 C CNN
	1    5600 4650
	0 -1 -1 0
$EndComp
Text Label 5150 4650 0    35   ~ 0
SYS_I2C_SDA
Text Label 6050 4650 0    35   ~ 0
TOUCH_SDA
$Comp
L Device:R_Small R402
U 1 1 410004
P 5600 5200
F 0 "R402" H 5750 5300 50  0000 C CNN
F 1 "0R LINK" H 5850 5100 50  0000 C CNN
F 2 "" H 5600 5200 50  0001 C CNN
F 3 "~" H 5600 5200 50  0001 C CNN
	1    5600 5200
	0 -1 -1 0
$EndComp
Text Label 5150 5200 0    35   ~ 0
SYS_I2C_SCL
Text Label 6050 5200 0    35   ~ 0
TOUCH_SCL
$Comp
L Device:R_Small R403
U 1 1 410005
P 6800 4650
F 0 "R403" H 6950 4750 50  0000 C CNN
F 1 "4.7k PU PROV" H 7150 4550 50  0000 C CNN
F 2 "" H 6800 4650 50  0001 C CNN
F 3 "~" H 6800 4650 50  0001 C CNN
	1    6800 4650
	1 0 0 -1
$EndComp
Text Label 6800 4350 0    35   ~ 0
+1V8
Text Label 6800 4950 0    35   ~ 0
SYS_I2C_SDA
$Comp
L Device:R_Small R404
U 1 1 410006
P 7450 4650
F 0 "R404" H 7600 4750 50  0000 C CNN
F 1 "4.7k PU PROV" H 7800 4550 50  0000 C CNN
F 2 "" H 7450 4650 50  0001 C CNN
F 3 "~" H 7450 4650 50  0001 C CNN
	1    7450 4650
	1 0 0 -1
$EndComp
Text Label 7450 4350 0    35   ~ 0
+1V8
Text Label 7450 4950 0    35   ~ 0
SYS_I2C_SCL
$Comp
L Device:C_Small C401
U 1 1 410007
P 8300 4900
F 0 "C401" H 8450 5000 50  0000 C CNN
F 1 "100nF PROV" H 8600 4800 50  0000 C CNN
F 2 "" H 8300 4900 50  0001 C CNN
F 3 "~" H 8300 4900 50  0001 C CNN
	1    8300 4900
	1 0 0 -1
$EndComp
Text Label 8300 4650 0    35   ~ 0
TOUCH_VDD
Text Label 8300 5150 0    35   ~ 0
GND
Text Notes 4950 3900 0    45   ~ 0
R401/R402 are direct-I2C links only when the selected touch controller is 1.8V-I/O compatible.
Text Notes 4950 4050 0    42   ~ 0
If not compatible, DNP the links and insert a bidirectional level-shifter at the reserved touch interface.
Text Notes 4950 4200 0    42   ~ 0
R403/R404 are the single provisional SYS_I2C pull-up pair for Main Board; tune after bus-capacitance review.
Text Notes 700 700 0    48   ~ 0
r4 DISPLAY_TOUCH: logical AMOLED QSPI + reset/TE + touch I2C interface captured without inventing supplier FPC pinout.
Text Notes 700 850 0    42   ~ 0
Hard gate remains: exact panel/touch MPN, FPC drawing, DISP_SW voltage/current, TOUCH_VDD and I/O thresholds.
Text Notes 700 7350 0    36   ~ 0
WIRE_AUDIT_R4_BEGIN
Wire Wire Line
	2950 2550 3100 2550
Wire Wire Line
	2950 2650 3100 2650
Wire Wire Line
	2950 2750 3100 2750
Wire Wire Line
	2950 2850 3100 2850
Wire Wire Line
	2950 2950 3100 2950
Wire Wire Line
	2950 3050 3100 3050
Wire Wire Line
	2950 3150 3100 3150
Wire Wire Line
	2950 3250 3100 3250
Wire Wire Line
	2950 3350 3100 3350
Wire Wire Line
	2950 3450 3100 3450
Wire Wire Line
	2950 4750 3100 4750
Wire Wire Line
	2950 4850 3100 4850
Wire Wire Line
	2950 4950 3100 4950
Wire Wire Line
	2950 5050 3100 5050
Wire Wire Line
	2950 5150 3100 5150
Wire Wire Line
	2950 5250 3100 5250
Wire Wire Line
	5150 4650 5500 4650
Wire Wire Line
	5700 4650 6050 4650
Wire Wire Line
	5150 5200 5500 5200
Wire Wire Line
	5700 5200 6050 5200
Wire Wire Line
	6800 4350 6800 4550
Wire Wire Line
	6800 4750 6800 4950
Wire Wire Line
	7450 4350 7450 4550
Wire Wire Line
	7450 4750 7450 4950
Wire Wire Line
	8300 4650 8300 4800
Wire Wire Line
	8300 5000 8300 5150
Text Notes 700 7500 0    36   ~ 0
WIRE_AUDIT_R4_END
$EndSCHEMATC
