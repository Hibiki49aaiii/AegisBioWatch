EESchema Schematic File Version 4
LIBS:AegisBioWatch
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "AegisBioWatch PMIC / Charger"
Date "2026-08-08"
Rev "Rev.0 / Phase 1 r6"
Comp "AegisBioWatch"
Comment1 "nPM1300 full passive capture - ERC pending"
Comment2 "PCB release prohibited until remaining freeze gates close"
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L AegisBioWatch:nPM1300-QEXX U2
U 1 1 AC76FD
P 5200 3850
F 0 "U2" H 5350 3950 50  0000 C CNN
F 1 "nPM1300-QEXX" H 5450 3750 50  0000 C CNN
F 2 "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm_ThermalVias" H 5200 3850 50  0001 C CNN
F 3 "https://docs.nordicsemi.com/bundle/ps_npm1300" H 5200 3850 50  0001 C CNN
	1    5200 3850
	1 0 0 -1
$EndComp
Text Label 4250 2750 0    35   ~ 0
+1V8
Text Label 4250 2885 0    35   ~ 0
PVSS1_LOCAL
Text Label 4250 3020 0    35   ~ 0
PMIC_SW1
Text Label 4250 3155 0    35   ~ 0
VSYS
Text Label 4250 3290 0    35   ~ 0
PMIC_SW2
Text Label 4250 3425 0    35   ~ 0
PVSS2_LOCAL
Text Label 4250 3560 0    35   ~ 0
PMIC_INT
Text Label 4250 3695 0    35   ~ 0
PMIC_GPIO1
Text Label 4250 3830 0    35   ~ 0
PMIC_GPIO2
Text Label 4250 3965 0    35   ~ 0
PMIC_GPIO3
Text Label 4250 4100 0    35   ~ 0
PMIC_GPIO4
Text Label 4250 4235 0    35   ~ 0
+1V8
Text Label 4250 4370 0    35   ~ 0
SYS_I2C_SDA
Text Label 4250 4505 0    35   ~ 0
SYS_I2C_SCL
Text Label 4250 4640 0    35   ~ 0
SHIP_HOLD
Text Label 4250 4775 0    35   ~ 0
PMIC_VSET2
Text Label 4250 4910 0    35   ~ 0
PMIC_VSET1
Text Label 6150 2750 2    35   ~ 0
BAT_NTC
Text Label 6150 2885 2    35   ~ 0
VBAT
Text Label 6150 3020 2    35   ~ 0
VSYS
Text Label 6150 3155 2    35   ~ 0
CHG_5V
Text Label 6150 3290 2    35   ~ 0
VBUSOUT_SENSE
Text Label 6150 3425 2    35   ~ 0
CC1_NC
Text Label 6150 3560 2    35   ~ 0
CC2_NC
Text Label 6150 3695 2    35   ~ 0
PMIC_LED0
Text Label 6150 3830 2    35   ~ 0
PMIC_LED1
Text Label 6150 3965 2    35   ~ 0
PMIC_LED2
Text Label 6150 4100 2    35   ~ 0
LDO1_IN
Text Label 6150 4235 2    35   ~ 0
DISP_SW
Text Label 6150 4370 2    35   ~ 0
LDO2_IN
Text Label 6150 4505 2    35   ~ 0
BIO_SW
Text Label 6150 4640 2    35   ~ 0
+3V0
Text Label 6150 4775 2    35   ~ 0
GND
$Comp
L Device:L_Small L101
U 1 1 130358
P 7800 2200
F 0 "L101" H 7950 2300 50  0000 C CNN
F 1 "2.2uH / DCR<400mR" H 8050 2100 50  0000 C CNN
F 2 "Inductor_SMD:L_0805_2012Metric" H 7800 2200 50  0001 C CNN
F 3 "~" H 7800 2200 50  0001 C CNN
	1    7800 2200
	0 -1 -1 0
$EndComp
Text Label 7450 2200 2    35   ~ 0
PMIC_SW1
Text Label 8150 2200 0    35   ~ 0
+1V8
Wire Wire Line
	7450 2200 7700 2200
Wire Wire Line
	7900 2200 8150 2200
$Comp
L Device:L_Small L102
U 1 1 225768
P 7800 2950
F 0 "L102" H 7950 3050 50  0000 C CNN
F 1 "2.2uH / DCR<400mR" H 8050 2850 50  0000 C CNN
F 2 "Inductor_SMD:L_0805_2012Metric" H 7800 2950 50  0001 C CNN
F 3 "~" H 7800 2950 50  0001 C CNN
	1    7800 2950
	0 -1 -1 0
$EndComp
Text Label 7450 2950 2    35   ~ 0
PMIC_SW2
Text Label 8150 2950 0    35   ~ 0
+3V0
Wire Wire Line
	7450 2950 7700 2950
Wire Wire Line
	7900 2950 8150 2950
$Comp
L Device:R_Small R101
U 1 1 C978FA
P 7500 3650
F 0 "R101" H 7650 3750 50  0000 C CNN
F 1 "47k 1%" H 7750 3550 50  0000 C CNN
F 2 "Resistor_SMD:R_0201_0603Metric" H 7500 3650 50  0001 C CNN
F 3 "~" H 7500 3650 50  0001 C CNN
	1    7500 3650
	1 0 0 -1
$EndComp
Text Label 7500 3350 0    35   ~ 0
PMIC_VSET1
Text Label 7500 3950 0    35   ~ 0
GND
Wire Wire Line
	7500 3350 7500 3550
Wire Wire Line
	7500 3750 7500 3950
$Comp
L Device:R_Small R102
U 1 1 30B340
P 8200 3650
F 0 "R102" H 8350 3750 50  0000 C CNN
F 1 "150k 1%" H 8450 3550 50  0000 C CNN
F 2 "Resistor_SMD:R_0201_0603Metric" H 8200 3650 50  0001 C CNN
F 3 "~" H 8200 3650 50  0001 C CNN
	1    8200 3650
	1 0 0 -1
$EndComp
Text Label 8200 3350 0    35   ~ 0
PMIC_VSET2
Text Label 8200 3950 0    35   ~ 0
GND
Wire Wire Line
	8200 3350 8200 3550
Wire Wire Line
	8200 3750 8200 3950
$Comp
L Device:C_Small C101
U 1 1 A0E90F
P 1750 1750
F 0 "C101" H 1900 1850 50  0000 C CNN
F 1 "1.0uF X5R 10V" H 2000 1650 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 1750 1750 50  0001 C CNN
F 3 "~" H 1750 1750 50  0001 C CNN
	1    1750 1750
	1 0 0 -1
$EndComp
Text Label 1750 1450 0    35   ~ 0
CHG_5V
Text Label 1750 2050 0    35   ~ 0
GND
Wire Wire Line
	1750 1450 1750 1650
Wire Wire Line
	1750 1850 1750 2050
$Comp
L Device:C_Small C102
U 1 1 63DF15
P 2250 1750
F 0 "C102" H 2400 1850 50  0000 C CNN
F 1 "10uF X5R 25V" H 2500 1650 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 2250 1750 50  0001 C CNN
F 3 "~" H 2250 1750 50  0001 C CNN
	1    2250 1750
	1 0 0 -1
$EndComp
Text Label 2250 1450 0    35   ~ 0
VSYS
Text Label 2250 2050 0    35   ~ 0
GND
Wire Wire Line
	2250 1450 2250 1650
Wire Wire Line
	2250 1850 2250 2050
$Comp
L Device:C_Small C103
U 1 1 130752
P 2750 1750
F 0 "C103" H 2900 1850 50  0000 C CNN
F 1 "10uF X5R 25V" H 3000 1650 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 2750 1750 50  0001 C CNN
F 3 "~" H 2750 1750 50  0001 C CNN
	1    2750 1750
	1 0 0 -1
$EndComp
Text Label 2750 1450 0    35   ~ 0
VSYS
Text Label 2750 2050 0    35   ~ 0
PVSS1_LOCAL
Wire Wire Line
	2750 1450 2750 1650
Wire Wire Line
	2750 1850 2750 2050
$Comp
L Device:C_Small C104
U 1 1 75D687
P 3250 1750
F 0 "C104" H 3400 1850 50  0000 C CNN
F 1 "10uF X5R 25V" H 3500 1650 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 3250 1750 50  0001 C CNN
F 3 "~" H 3250 1750 50  0001 C CNN
	1    3250 1750
	1 0 0 -1
$EndComp
Text Label 3250 1450 0    35   ~ 0
VSYS
Text Label 3250 2050 0    35   ~ 0
PVSS2_LOCAL
Wire Wire Line
	3250 1450 3250 1650
Wire Wire Line
	3250 1850 3250 2050
$Comp
L Device:C_Small C105
U 1 1 C4E82F
P 3750 1750
F 0 "C105" H 3900 1850 50  0000 C CNN
F 1 "1.0uF X5R 10V" H 4000 1650 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 3750 1750 50  0001 C CNN
F 3 "~" H 3750 1750 50  0001 C CNN
	1    3750 1750
	1 0 0 -1
$EndComp
Text Label 3750 1450 0    35   ~ 0
VBUSOUT_SENSE
Text Label 3750 2050 0    35   ~ 0
GND
Wire Wire Line
	3750 1450 3750 1650
Wire Wire Line
	3750 1850 3750 2050
$Comp
L Device:C_Small C106
U 1 1 64AE10
P 4250 1750
F 0 "C106" H 4400 1850 50  0000 C CNN
F 1 "2.2uF X7R 16V" H 4500 1650 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 4250 1750 50  0001 C CNN
F 3 "~" H 4250 1750 50  0001 C CNN
	1    4250 1750
	1 0 0 -1
$EndComp
Text Label 4250 1450 0    35   ~ 0
VBAT
Text Label 4250 2050 0    35   ~ 0
GND
Wire Wire Line
	4250 1450 4250 1650
Wire Wire Line
	4250 1850 4250 2050
$Comp
L Device:C_Small C107
U 1 1 C6CF59
P 8750 2200
F 0 "C107" H 8900 2300 50  0000 C CNN
F 1 "10uF X5R 25V" H 9000 2100 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 8750 2200 50  0001 C CNN
F 3 "~" H 8750 2200 50  0001 C CNN
	1    8750 2200
	1 0 0 -1
$EndComp
Text Label 8750 1900 0    35   ~ 0
+1V8
Text Label 8750 2500 0    35   ~ 0
PVSS1_LOCAL
Wire Wire Line
	8750 1900 8750 2100
Wire Wire Line
	8750 2300 8750 2500
$Comp
L Device:C_Small C108
U 1 1 001A5F
P 8750 2950
F 0 "C108" H 8900 3050 50  0000 C CNN
F 1 "10uF X5R 25V" H 9000 2850 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 8750 2950 50  0001 C CNN
F 3 "~" H 8750 2950 50  0001 C CNN
	1    8750 2950
	1 0 0 -1
$EndComp
Text Label 8750 2650 0    35   ~ 0
+3V0
Text Label 8750 3250 0    35   ~ 0
PVSS2_LOCAL
Wire Wire Line
	8750 2650 8750 2850
Wire Wire Line
	8750 3050 8750 3250
$Comp
L Device:C_Small C109
U 1 1 421885
P 7350 5050
F 0 "C109" H 7500 5150 50  0000 C CNN
F 1 "10uF X5R 25V" H 7600 4950 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 7350 5050 50  0001 C CNN
F 3 "~" H 7350 5050 50  0001 C CNN
	1    7350 5050
	1 0 0 -1
$EndComp
Text Label 7350 4750 0    35   ~ 0
DISP_SW
Text Label 7350 5350 0    35   ~ 0
GND
Wire Wire Line
	7350 4750 7350 4950
Wire Wire Line
	7350 5150 7350 5350
$Comp
L Device:C_Small C110
U 1 1 DC6FFA
P 7750 5050
F 0 "C110" H 7900 5150 50  0000 C CNN
F 1 "10uF X5R 25V" H 8000 4950 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 7750 5050 50  0001 C CNN
F 3 "~" H 7750 5050 50  0001 C CNN
	1    7750 5050
	1 0 0 -1
$EndComp
Text Label 7750 4750 0    35   ~ 0
DISP_SW
Text Label 7750 5350 0    35   ~ 0
GND
Wire Wire Line
	7750 4750 7750 4950
Wire Wire Line
	7750 5150 7750 5350
$Comp
L Device:C_Small C111
U 1 1 44B802
P 8350 5050
F 0 "C111" H 8500 5150 50  0000 C CNN
F 1 "10uF X5R 25V" H 8600 4950 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 8350 5050 50  0001 C CNN
F 3 "~" H 8350 5050 50  0001 C CNN
	1    8350 5050
	1 0 0 -1
$EndComp
Text Label 8350 4750 0    35   ~ 0
BIO_SW
Text Label 8350 5350 0    35   ~ 0
GND
Wire Wire Line
	8350 4750 8350 4950
Wire Wire Line
	8350 5150 8350 5350
$Comp
L Device:C_Small C112
U 1 1 931598
P 8750 5050
F 0 "C112" H 8900 5150 50  0000 C CNN
F 1 "10uF X5R 25V" H 9000 4950 50  0000 C CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 8750 5050 50  0001 C CNN
F 3 "~" H 8750 5050 50  0001 C CNN
	1    8750 5050
	1 0 0 -1
$EndComp
Text Label 8750 4750 0    35   ~ 0
BIO_SW
Text Label 8750 5350 0    35   ~ 0
GND
Wire Wire Line
	8750 4750 8750 4950
Wire Wire Line
	8750 5150 8750 5350
$Comp
L Device:C_Small C113
U 1 1 14E9FE
P 9250 5050
F 0 "C113" H 9400 5150 50  0000 C CNN
F 1 "100nF X5R" H 9500 4950 50  0000 C CNN
F 2 "Capacitor_SMD:C_0201_0603Metric" H 9250 5050 50  0001 C CNN
F 3 "~" H 9250 5050 50  0001 C CNN
	1    9250 5050
	1 0 0 -1
$EndComp
Text Label 9250 4750 0    35   ~ 0
+1V8
Text Label 9250 5350 0    35   ~ 0
GND
Wire Wire Line
	9250 4750 9250 4950
Wire Wire Line
	9250 5150 9250 5350
$Comp
L Device:C_Small C114
U 1 1 6856B2
P 4750 1750
F 0 "C114" H 4900 1850 50  0000 C CNN
F 1 "100nF HF / APP" H 5000 1650 50  0000 C CNN
F 2 "Capacitor_SMD:C_0201_0603Metric" H 4750 1750 50  0001 C CNN
F 3 "~" H 4750 1750 50  0001 C CNN
	1    4750 1750
	1 0 0 -1
$EndComp
Text Label 4750 1450 0    35   ~ 0
VSYS
Text Label 4750 2050 0    35   ~ 0
GND
Wire Wire Line
	4750 1450 4750 1650
Wire Wire Line
	4750 1850 4750 2050
$Comp
L Device:Net-Tie_2 NT101
U 1 1 A37A3C
P 6900 2450
F 0 "NT101" H 7050 2550 50  0000 C CNN
F 1 "PVSS1_NET_TIE" H 7150 2350 50  0000 C CNN
F 2 "" H 6900 2450 50  0001 C CNN
F 3 "~" H 6900 2450 50  0001 C CNN
	1    6900 2450
	0 -1 -1 0
$EndComp
Text Label 6550 2450 2    35   ~ 0
PVSS1_LOCAL
Text Label 7250 2450 0    35   ~ 0
GND
Wire Wire Line
	6550 2450 6800 2450
Wire Wire Line
	7000 2450 7250 2450
$Comp
L Device:Net-Tie_2 NT102
U 1 1 19883F
P 6900 3200
F 0 "NT102" H 7050 3300 50  0000 C CNN
F 1 "PVSS2_NET_TIE" H 7150 3100 50  0000 C CNN
F 2 "" H 6900 3200 50  0001 C CNN
F 3 "~" H 6900 3200 50  0001 C CNN
	1    6900 3200
	0 -1 -1 0
$EndComp
Text Label 6550 3200 2    35   ~ 0
PVSS2_LOCAL
Text Label 7250 3200 0    35   ~ 0
GND
Wire Wire Line
	6550 3200 6800 3200
Wire Wire Line
	7000 3200 7250 3200
$Comp
L Device:R_Small R105
U 1 1 CFCF15
P 7350 4350
F 0 "R105" H 7500 4450 50  0000 C CNN
F 1 "0R DNP/OPTION" H 7600 4250 50  0000 C CNN
F 2 "Resistor_SMD:R_0201_0603Metric" H 7350 4350 50  0001 C CNN
F 3 "~" H 7350 4350 50  0001 C CNN
	1    7350 4350
	0 -1 -1 0
$EndComp
Text Label 7000 4350 2    35   ~ 0
VSYS
Text Label 7700 4350 0    35   ~ 0
LDO1_IN
Wire Wire Line
	7000 4350 7250 4350
Wire Wire Line
	7450 4350 7700 4350
$Comp
L Device:R_Small R106
U 1 1 37975D
P 8350 4350
F 0 "R106" H 8500 4450 50  0000 C CNN
F 1 "0R DNP/OPTION" H 8600 4250 50  0000 C CNN
F 2 "Resistor_SMD:R_0201_0603Metric" H 8350 4350 50  0001 C CNN
F 3 "~" H 8350 4350 50  0001 C CNN
	1    8350 4350
	0 -1 -1 0
$EndComp
Text Label 8000 4350 2    35   ~ 0
VSYS
Text Label 8700 4350 0    35   ~ 0
LDO2_IN
Wire Wire Line
	8000 4350 8250 4350
Wire Wire Line
	8450 4350 8700 4350
$Comp
L Device:R_Small R103
U 1 1 298982
P 2450 4450
F 0 "R103" H 2600 4550 50  0000 C CNN
F 1 "10k DNP/TUNE" H 2700 4350 50  0000 C CNN
F 2 "Resistor_SMD:R_0201_0603Metric" H 2450 4450 50  0001 C CNN
F 3 "~" H 2450 4450 50  0001 C CNN
	1    2450 4450
	1 0 0 -1
$EndComp
Text Label 2450 4150 0    35   ~ 0
+1V8
Text Label 2450 4750 0    35   ~ 0
SYS_I2C_SDA
Wire Wire Line
	2450 4150 2450 4350
Wire Wire Line
	2450 4550 2450 4750
$Comp
L Device:R_Small R104
U 1 1 847C05
P 2950 4450
F 0 "R104" H 3100 4550 50  0000 C CNN
F 1 "10k DNP/TUNE" H 3200 4350 50  0000 C CNN
F 2 "Resistor_SMD:R_0201_0603Metric" H 2950 4450 50  0001 C CNN
F 3 "~" H 2950 4450 50  0001 C CNN
	1    2950 4450
	1 0 0 -1
$EndComp
Text Label 2950 4150 0    35   ~ 0
+1V8
Text Label 2950 4750 0    35   ~ 0
SYS_I2C_SCL
Wire Wire Line
	2950 4150 2950 4350
Wire Wire Line
	2950 4550 2950 4750
$Comp
L Connector_Generic:Conn_01x03 J2
U 1 1 487111
P 1600 5750
F 0 "J2" H 1750 5850 50  0000 C CNN
F 1 "BATTERY_PACK_300mAh_3WIRE" H 2050 5650 50  0000 C CNN
F 2 "" H 1600 5750 50  0001 C CNN
F 3 "~" H 1600 5750 50  0001 C CNN
	1    1600 5750
	1 0 0 -1
$EndComp
Text Label 1250 5650 0    35   ~ 0
VBAT
Text Label 1250 5750 0    35   ~ 0
BAT_NTC
Text Label 1250 5850 0    35   ~ 0
GND
Wire Wire Line
	1250 5650 1400 5650
Wire Wire Line
	1250 5750 1400 5750
Wire Wire Line
	1250 5850 1400 5850
$Comp
L Connector_Generic:Conn_01x02 J3
U 1 1 094F64
P 1600 6350
F 0 "J3" H 1750 6450 50  0000 C CNN
F 1 "MAG_DOCK_RAW_5V" H 1900 6250 50  0000 C CNN
F 2 "" H 1600 6350 50  0001 C CNN
F 3 "~" H 1600 6350 50  0001 C CNN
	1    1600 6350
	1 0 0 -1
$EndComp
Text Label 1250 6350 0    35   ~ 0
DOCK_5V_RAW
Text Label 1250 6450 0    35   ~ 0
GND
Wire Wire Line
	1250 6350 1400 6350
Wire Wire Line
	1250 6450 1400 6450
$Comp
L Connector_Generic:Conn_01x02 J101
U 1 1 8FA624
P 3400 5900
F 0 "J101" H 3550 6000 50  0000 C CNN
F 1 "SHIP_WAKE_BUTTON" H 3650 5800 50  0000 C CNN
F 2 "" H 3400 5900 50  0001 C CNN
F 3 "~" H 3400 5900 50  0001 C CNN
	1    3400 5900
	1 0 0 -1
$EndComp
Text Label 3000 5900 0    35   ~ 0
SHIP_HOLD
Text Label 3000 6000 0    35   ~ 0
GND
Wire Wire Line
	3000 5900 3200 5900
Wire Wire Line
	3000 6000 3200 6000
Text Notes 650 650 0    48   ~ 0
r5: nPM1300 QFN32 full functional passive network captured from current Nordic guidance.
Text Notes 650 800 0    42   ~ 0
Config: BUCK1 1.8V (47k), BUCK2 3.0V (150k), 2.2uH inductors, local PVSS net-ties.
Text Notes 650 950 0    42   ~ 0
VBUSOUT 1uF is fitted even if unused. VBAT=2.2uF. VDDIO=100nF. VSYS/PVDD receive 10uF-class local decoupling.
Text Notes 650 1100 0    42   ~ 0
RF-sensitive application addition: C114 100nF close to PVDD/VSYS; second layer must remain solid GND.
Text Notes 650 1250 0    42   ~ 0
DISP_SW/BIO_SW are PROVISIONAL LS/LDO outputs: 50mA max in LDO mode, 100mA in load-switch mode.
Text Notes 650 1400 0    42   ~ 0
PVSS1/PVSS2 net-ties mirror the Nordic QFN reference intent: local top-layer return into a CONTINUOUS L2 GND plane, not a split plane.
Text Notes 650 1550 0    42   ~ 0
Do not approve DISP_SW/BIO_SW for panel/PPG loads until peak-current and startup/inrush budgets are measured.
Text Notes 650 1700 0    42   ~ 0
R105/R106 are 0R OPTION links from VSYS to VINLDO1/2; populate only after final LS/LDO mode decision.
Text Notes 650 1850 0    42   ~ 0
Magnetic dock is not USB-C. CC1/CC2 remain unused; default VBUS input-current limit is 100mA after reset/attach.
Text Notes 650 2000 0    42   ~ 0
Exact dock ESD/reverse-polarity device MPNs, battery cell/NTC, and charge current remain hard release gates.
Text Notes 650 2150 0    42   ~ 0
nPM1300 Rev.1 build-code errata must be checked against the procured lot before LDO/charger firmware freeze.
Text Notes 650 2300 0    42   ~ 0
Bio-electrode acquisition remains inhibited whenever external charging is present or charge state is uncertain.
$Comp
L AegisBioWatch:PMEG2010AEJ D101
U 1 1 610101
P 3050 6550
F 0 "D101" H 3050 6750 50  0000 C CNN
F 1 "PMEG2010AEJ" H 3050 6350 50  0000 C CNN
F 2 "Diode_SMD:D_SOD-323F" H 3050 6250 50  0001 C CNN
F 3 "https://www.nexperia.com/product/PMEG2010AEJ" H 3050 6150 50  0001 C CNN
	1    3050 6550
	1 0 0 -1
$EndComp
Text Label 2500 6550 2    35   ~ 0
DOCK_5V_RAW
Text Label 3600 6550 0    35   ~ 0
CHG_5V
Wire Wire Line
	2500 6550 2650 6550
Wire Wire Line
	3450 6550 3600 6550
$Comp
L AegisBioWatch:PESD5V0S1UL D102
U 1 1 610102
P 3050 7050
F 0 "D102" H 3050 7250 50  0000 C CNN
F 1 "PESD5V0S1UL" H 3050 6850 50  0000 C CNN
F 2 "AegisBioWatch:SOD882_PESD5V0S1UL_VERIFY" H 3050 6750 50  0001 C CNN
F 3 "https://www.nexperia.com/product/PESD5V0S1UL" H 3050 6650 50  0001 C CNN
	1    3050 7050
	1 0 0 -1
$EndComp
Text Label 2500 7050 2    35   ~ 0
GND
Text Label 3600 7050 0    35   ~ 0
DOCK_5V_RAW
Wire Wire Line
	2500 7050 2650 7050
Wire Wire Line
	3450 7050 3600 7050
Text Notes 650 2450 0    42   ~ 0
r6 battery cell candidate: EEMB LP372435TB, 3.7V/300mAh, 24.5x36x4.0mm. It is a bare cell and MUST NOT connect directly without pack protection.
Text Notes 650 2600 0    42   ~ 0
Battery pack spec: cell + OV/UV/overcurrent protection + thermally coupled 10k NTC. Preferred NTC: Murata NXRT15XH103FA5B030 (B25/50=3380K).
Text Notes 650 2750 0    42   ~ 0
r6 dock protection: DOCK_5V_RAW -> PMEG2010AEJ Schottky -> CHG_5V; PESD5V0S1UL shunts ESD at raw dock node. Mechanical keying remains mandatory.
$EndSCHEMATC
