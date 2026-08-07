EESchema Schematic File Version 4
LIBS:AegisBioWatch
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "AegisBioWatch PMIC / Charger"
Date "2026-08-07"
Rev "Rev.0 / Phase 1 r4"
Comp "AegisBioWatch"
Comment1 "CAPTURE DRAFT - ERC pending"
Comment2 "PCB release prohibited until reference gates close"
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L AegisBioWatch:nPM1300-QEXX U2
U 1 1 6485E5
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
GND
Text Label 4250 3020 0    35   ~ 0
PMIC_SW1
Text Label 4250 3155 0    35   ~ 0
VSYS
Text Label 4250 3290 0    35   ~ 0
PMIC_SW2
Text Label 4250 3425 0    35   ~ 0
GND
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
VBUSOUT_NC
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
VSYS
Text Label 6150 4235 2    35   ~ 0
DISP_SW
Text Label 6150 4370 2    35   ~ 0
VSYS
Text Label 6150 4505 2    35   ~ 0
BIO_SW
Text Label 6150 4640 2    35   ~ 0
+3V0
Text Label 6150 4775 2    35   ~ 0
GND
$Comp
L Device:L_Small L101
U 1 1 3D601D
P 7800 2750
F 0 "L101" H 7950 2850 50  0000 C CNN
F 1 "2.2uH" H 8050 2650 50  0000 C CNN
F 2 "" H 7800 2750 50  0001 C CNN
F 3 "~" H 7800 2750 50  0001 C CNN
	1    7800 2750
	0 -1 -1 0
$EndComp
Text Label 7500 2750 2    35   ~ 0
PMIC_SW1
Text Label 8100 2750 0    35   ~ 0
+1V8
$Comp
L Device:L_Small L102
U 1 1 F00B74
P 7800 3900
F 0 "L102" H 7950 4000 50  0000 C CNN
F 1 "2.2uH" H 8050 3800 50  0000 C CNN
F 2 "" H 7800 3900 50  0001 C CNN
F 3 "~" H 7800 3900 50  0001 C CNN
	1    7800 3900
	0 -1 -1 0
$EndComp
Text Label 7500 3900 2    35   ~ 0
PMIC_SW2
Text Label 8100 3900 0    35   ~ 0
+3V0
$Comp
L Device:R_Small R101
U 1 1 BF22D2
P 7400 4800
F 0 "R101" H 7550 4900 50  0000 C CNN
F 1 "47k 1%" H 7650 4700 50  0000 C CNN
F 2 "" H 7400 4800 50  0001 C CNN
F 3 "~" H 7400 4800 50  0001 C CNN
	1    7400 4800
	1 0 0 -1
$EndComp
Text Label 7400 4500 0    35   ~ 0
PMIC_VSET1
Text Label 7400 5100 0    35   ~ 0
GND
$Comp
L Device:R_Small R102
U 1 1 5E9D2C
P 8100 4800
F 0 "R102" H 8250 4900 50  0000 C CNN
F 1 "150k 1%" H 8350 4700 50  0000 C CNN
F 2 "" H 8100 4800 50  0001 C CNN
F 3 "~" H 8100 4800 50  0001 C CNN
	1    8100 4800
	1 0 0 -1
$EndComp
Text Label 8100 4500 0    35   ~ 0
PMIC_VSET2
Text Label 8100 5100 0    35   ~ 0
GND
$Comp
L Connector_Generic:Conn_01x03 J2
U 1 1 289A5B
P 1800 2500
F 0 "J2" H 1950 2600 50  0000 C CNN
F 1 "BATTERY_1S_NTC" H 2050 2400 50  0000 C CNN
F 2 "" H 1800 2500 50  0001 C CNN
F 3 "~" H 1800 2500 50  0001 C CNN
	1    1800 2500
	1 0 0 -1
$EndComp
Text Label 1500 2400 0    35   ~ 0
VBAT
Text Label 1500 2500 0    35   ~ 0
BAT_NTC
Text Label 1500 2600 0    35   ~ 0
GND
$Comp
L Connector_Generic:Conn_01x02 J3
U 1 1 D776F5
P 1800 3250
F 0 "J3" H 1950 3400 50  0000 C CNN
F 1 "MAG_DOCK_5V" H 2050 3200 50  0000 C CNN
F 2 "" H 1800 3300 50  0001 C CNN
F 3 "~" H 1800 3300 50  0001 C CNN
	1    1800 3250
	1 0 0 -1
$EndComp
Text Label 1500 3250 0    35   ~ 0
CHG_5V
Text Label 1500 3350 0    35   ~ 0
GND
Text Notes 700 700 0    50   ~ 0
U2 QFN32 pad map captured. BUCK1=1.8V via VSET1 47k; BUCK2=3.0V via VSET2 150k; both use 2.2uH.
Text Notes 700 850 0    50   ~ 0
Magnetic 5V dock is not USB-C. CC1/CC2 remain unused; VBUS current-limit policy is firmware-controlled after boot.
Text Notes 700 1000 0    50   ~ 0
GATE: final battery/NTC curve, input ESD/surge parts, exact charge-current policy and output capacitor MPNs.
Text Notes 700 1150 0    50   ~ 0
Bio-electrode acquisition remains inhibited whenever external charging is detected.
Text Notes 700 7350 0    36   ~ 0
WIRE_AUDIT_R4_BEGIN
Wire Wire Line
	7500 2750 7700 2750
Wire Wire Line
	7900 2750 8100 2750
Wire Wire Line
	7500 3900 7700 3900
Wire Wire Line
	7900 3900 8100 3900
Wire Wire Line
	7400 4500 7400 4700
Wire Wire Line
	7400 4900 7400 5100
Wire Wire Line
	8100 4500 8100 4700
Wire Wire Line
	8100 4900 8100 5100
Wire Wire Line
	1500 2400 1600 2400
Wire Wire Line
	1500 2500 1600 2500
Wire Wire Line
	1500 2600 1600 2600
Wire Wire Line
	1500 3250 1600 3250
Wire Wire Line
	1500 3350 1600 3350
Text Notes 700 7500 0    36   ~ 0
WIRE_AUDIT_R4_END
$EndSCHEMATC
