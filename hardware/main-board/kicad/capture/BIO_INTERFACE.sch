EESchema Schematic File Version 4
LIBS:AegisBioWatch
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "AegisBioWatch Bio Board Interface"
Date "2026-08-07"
Rev "Rev.0 / Phase 1 r4"
Comp "AegisBioWatch"
Comment1 "LOGICAL CONNECTOR CAPTURE - physical connector not frozen"
Comment2 "Charging-state safety defaults to inhibit"
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector_Generic:Conn_02x10_Odd_Even J7
U 1 1 510001
P 3600 3600
F 0 "J7" H 3650 4200 50  0000 C CNN
F 1 "MAIN_BIO_LOGIC_20" H 3650 3000 50  0000 C CNN
F 2 "" H 3600 3600 50  0001 C CNN
F 3 "~" H 3600 3600 50  0001 C CNN
	1    3600 3600
	1 0 0 -1
$EndComp
Text Label 3150 3150 2    35   ~ 0
GND
Text Label 3150 3250 2    35   ~ 0
+1V8
Text Label 3150 3350 2    35   ~ 0
SYS_I2C_SDA
Text Label 3150 3450 2    35   ~ 0
GND
Text Label 3150 3550 2    35   ~ 0
AUX_SPI_MOSI
Text Label 3150 3650 2    35   ~ 0
BIO_SPI_CS_N
Text Label 3150 3750 2    35   ~ 0
PPG_INT_N
Text Label 3150 3850 2    35   ~ 0
IMU_INT1
Text Label 3150 3950 2    35   ~ 0
BIO_SAFE_EN
Text Label 3150 4050 2    35   ~ 0
GPIO_SPARE0
Text Label 4150 3150 0    35   ~ 0
BIO_SW
Text Label 4150 3250 0    35   ~ 0
GND
Text Label 4150 3350 0    35   ~ 0
SYS_I2C_SCL
Text Label 4150 3450 0    35   ~ 0
AUX_SPI_SCK
Text Label 4150 3550 0    35   ~ 0
AUX_SPI_MISO
Text Label 4150 3650 0    35   ~ 0
GND
Text Label 4150 3750 0    35   ~ 0
EDA_INT_N
Text Label 4150 3850 0    35   ~ 0
IMU_INT2
Text Label 4150 3950 0    35   ~ 0
CHG_PRESENT_N
Text Label 4150 4050 0    35   ~ 0
SPARE_CLK_GPIO
Text Notes 1800 2600 0    45   ~ 0
J7 pin allocation is logical only; final board-to-board/FPC connector series and physical pin order remain a freeze gate.
Text Notes 1800 2750 0    42   ~ 0
BIO_SW is the switched Bio power domain. Do not bypass it with raw +3V0 on the Bio connector.
$Comp
L Device:R_Small R501
U 1 1 510002
P 6500 3300
F 0 "R501" H 6650 3400 50  0000 C CNN
F 1 "100k" H 6750 3200 50  0000 C CNN
F 2 "" H 6500 3300 50  0001 C CNN
F 3 "~" H 6500 3300 50  0001 C CNN
	1    6500 3300
	0 -1 -1 0
$EndComp
Text Label 6050 3300 2    35   ~ 0
CHG_5V
Text Label 6950 3300 0    35   ~ 0
CHG_SENSE_GATE
$Comp
L Device:R_Small R502
U 1 1 510003
P 6950 3850
F 0 "R502" H 7100 3950 50  0000 C CNN
F 1 "1M PD" H 7200 3750 50  0000 C CNN
F 2 "" H 6950 3850 50  0001 C CNN
F 3 "~" H 6950 3850 50  0001 C CNN
	1    6950 3850
	1 0 0 -1
$EndComp
Text Label 6950 3550 0    35   ~ 0
CHG_SENSE_GATE
Text Label 6950 4150 0    35   ~ 0
GND
$Comp
L Transistor_FET:2N7002 Q501
U 1 1 510004
P 7850 3850
F 0 "Q501" H 8050 3950 50  0000 L CNN
F 1 "2N7002-CLASS" H 8050 3750 50  0000 L CNN
F 2 "" H 8050 3775 50  0001 L CIN
F 3 "~" H 7850 3850 50  0001 L CNN
	1    7850 3850
	1 0 0 -1
$EndComp
Text Label 7550 3850 2    35   ~ 0
CHG_SENSE_GATE
Text Label 7950 4200 0    35   ~ 0
GND
Text Label 7950 3500 0    35   ~ 0
CHG_PRESENT_N
$Comp
L Device:R_Small R503
U 1 1 510005
P 8600 3300
F 0 "R503" H 8750 3400 50  0000 C CNN
F 1 "47k PU" H 8850 3200 50  0000 C CNN
F 2 "" H 8600 3300 50  0001 C CNN
F 3 "~" H 8600 3300 50  0001 C CNN
	1    8600 3300
	1 0 0 -1
$EndComp
Text Label 8600 3000 0    35   ~ 0
+1V8
Text Label 8600 3600 0    35   ~ 0
CHG_PRESENT_N
Text Notes 5900 2500 0    45   ~ 0
Hardware charge-present path: CHG_5V drives Q501; CHG_PRESENT_N is pulled to +1V8 and goes LOW during charging.
Text Notes 5900 2650 0    42   ~ 0
This path is independent of MCU firmware. Bio Board must treat LOW, missing power, or BIO_SAFE_EN=LOW as acquisition inhibit.
Text Notes 5900 2800 0    42   ~ 0
Q501/R501-R503 are logic safety signaling only, not medical isolation. Electrode disconnect/high-Z is implemented on Bio Board.
Text Notes 700 700 0    48   ~ 0
r4 BIO_INTERFACE: 20-signal logical interface + independent active-low charge-present safety signal captured.
Text Notes 700 850 0    42   ~ 0
Hard gate remains: physical connector/footprint, pin ordering, hot-plug behavior, ESD, and Bio Board electrode-disconnect implementation.
$EndSCHEMATC
