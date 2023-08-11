EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 6 7
Title "4-Port USB HUB for AvenaShield"
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:Crystal Y1
U 1 1 5E41C6AC
P 2750 3200
F 0 "Y1" V 2704 3331 50  0000 L CNN
F 1 "24 MHz " V 2795 3331 50  0000 L CNN
F 2 "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm" H 2750 3200 50  0001 C CNN
F 3 "~" H 2750 3200 50  0001 C CNN
	1    2750 3200
	0    1    1    0   
$EndComp
Wire Wire Line
	4050 3050 3200 3050
Wire Wire Line
	3200 3050 3200 3400
Wire Wire Line
	3200 3400 2750 3400
Wire Wire Line
	2750 3400 2750 3350
Wire Wire Line
	2350 2950 2750 2950
Wire Wire Line
	2350 3050 2350 2950
Wire Wire Line
	2750 3050 2750 2950
Connection ~ 2750 2950
Wire Wire Line
	2750 2950 4050 2950
$Comp
L Device:C C1
U 1 1 5E423740
P 2000 2950
F 0 "C1" V 1748 2950 50  0000 C CNN
F 1 "18pF" V 1839 2950 50  0000 C CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 2038 2800 50  0001 C CNN
F 3 "~" H 2000 2950 50  0001 C CNN
	1    2000 2950
	0    1    1    0   
$EndComp
$Comp
L Device:C C2
U 1 1 5E423F05
P 2000 3400
F 0 "C2" V 1748 3400 50  0000 C CNN
F 1 "18pF" V 1839 3400 50  0000 C CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 2038 3250 50  0001 C CNN
F 3 "~" H 2000 3400 50  0001 C CNN
	1    2000 3400
	0    1    1    0   
$EndComp
$Comp
L Device:R_US R1
U 1 1 5E41F0DD
P 2350 3200
F 0 "R1" H 2418 3246 50  0000 L CNN
F 1 "1M" H 2418 3155 50  0000 L CNN
F 2 "Resistor_SMD:R_1206_3216Metric" V 2390 3190 50  0001 C CNN
F 3 "~" H 2350 3200 50  0001 C CNN
	1    2350 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	2150 3400 2350 3400
Connection ~ 2750 3400
Wire Wire Line
	2350 3350 2350 3400
Connection ~ 2350 3400
Wire Wire Line
	2350 3400 2750 3400
Wire Wire Line
	2150 2950 2350 2950
Connection ~ 2350 2950
Wire Wire Line
	1850 2950 1750 2950
Wire Wire Line
	1750 2950 1750 3400
Wire Wire Line
	1750 3400 1850 3400
$Comp
L power:GNDREF #PWR0101
U 1 1 5E4274DE
P 1750 3550
F 0 "#PWR0101" H 1750 3300 50  0001 C CNN
F 1 "GNDREF" H 1755 3377 50  0000 C CNN
F 2 "" H 1750 3550 50  0001 C CNN
F 3 "" H 1750 3550 50  0001 C CNN
	1    1750 3550
	1    0    0    -1  
$EndComp
Wire Wire Line
	1750 3550 1750 3400
Connection ~ 1750 3400
$Comp
L Device:C C3
U 1 1 5E42DEB0
P 2200 3900
F 0 "C3" H 2315 3946 50  0000 L CNN
F 1 "0.1uF" H 2315 3855 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 2238 3750 50  0001 C CNN
F 3 "~" H 2200 3900 50  0001 C CNN
	1    2200 3900
	1    0    0    -1  
$EndComp
$Comp
L power:GNDREF #PWR0102
U 1 1 5E42ECC1
P 2200 4100
F 0 "#PWR0102" H 2200 3850 50  0001 C CNN
F 1 "GNDREF" H 2205 3927 50  0000 C CNN
F 2 "" H 2200 4100 50  0001 C CNN
F 3 "" H 2200 4100 50  0001 C CNN
	1    2200 4100
	1    0    0    -1  
$EndComp
$Comp
L Device:C C4
U 1 1 5E42F785
P 2700 3900
F 0 "C4" H 2815 3946 50  0000 L CNN
F 1 "0.1uF" H 2815 3855 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 2738 3750 50  0001 C CNN
F 3 "~" H 2700 3900 50  0001 C CNN
	1    2700 3900
	1    0    0    -1  
$EndComp
$Comp
L power:GNDREF #PWR0103
U 1 1 5E43160E
P 2700 4100
F 0 "#PWR0103" H 2700 3850 50  0001 C CNN
F 1 "GNDREF" H 2705 3927 50  0000 C CNN
F 2 "" H 2700 4100 50  0001 C CNN
F 3 "" H 2700 4100 50  0001 C CNN
	1    2700 4100
	1    0    0    -1  
$EndComp
Wire Wire Line
	2700 4100 2700 4050
Wire Wire Line
	2200 4100 2200 4050
$Comp
L power:GNDREF #PWR0104
U 1 1 5E436A57
P 5150 4600
F 0 "#PWR0104" H 5150 4350 50  0001 C CNN
F 1 "GNDREF" H 5155 4427 50  0000 C CNN
F 2 "" H 5150 4600 50  0001 C CNN
F 3 "" H 5150 4600 50  0001 C CNN
	1    5150 4600
	1    0    0    -1  
$EndComp
Wire Wire Line
	5150 1350 5150 1000
Wire Wire Line
	5150 1000 5050 1000
Wire Wire Line
	4850 1000 4850 1350
Wire Wire Line
	5050 1350 5050 1000
Connection ~ 5050 1000
Wire Wire Line
	5050 1000 4950 1000
Wire Wire Line
	4950 1350 4950 1000
Connection ~ 4950 1000
Wire Wire Line
	4950 1000 4850 1000
$Comp
L Device:C C5
U 1 1 5E43B074
P 800 1350
F 0 "C5" H 915 1396 50  0000 L CNN
F 1 "0.1uF" H 915 1305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 838 1200 50  0001 C CNN
F 3 "~" H 800 1350 50  0001 C CNN
	1    800  1350
	1    0    0    -1  
$EndComp
$Comp
L Device:C C6
U 1 1 5E43B5FD
P 1250 1350
F 0 "C6" H 1365 1396 50  0000 L CNN
F 1 "0.1uF" H 1365 1305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 1288 1200 50  0001 C CNN
F 3 "~" H 1250 1350 50  0001 C CNN
	1    1250 1350
	1    0    0    -1  
$EndComp
$Comp
L Device:C C7
U 1 1 5E43BB70
P 1700 1350
F 0 "C7" H 1815 1396 50  0000 L CNN
F 1 "0.1uF" H 1815 1305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 1738 1200 50  0001 C CNN
F 3 "~" H 1700 1350 50  0001 C CNN
	1    1700 1350
	1    0    0    -1  
$EndComp
$Comp
L Device:C C8
U 1 1 5E43C048
P 2150 1350
F 0 "C8" H 2265 1396 50  0000 L CNN
F 1 "0.1uF" H 2265 1305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 2188 1200 50  0001 C CNN
F 3 "~" H 2150 1350 50  0001 C CNN
	1    2150 1350
	1    0    0    -1  
$EndComp
Wire Wire Line
	1250 1200 1250 1000
Connection ~ 1700 1000
Wire Wire Line
	1700 1200 1700 1000
Wire Wire Line
	2150 1200 2150 1000
$Comp
L power:GNDREF #PWR0105
U 1 1 5E43E3BB
P 1400 1650
F 0 "#PWR0105" H 1400 1400 50  0001 C CNN
F 1 "GNDREF" H 1405 1477 50  0000 C CNN
F 2 "" H 1400 1650 50  0001 C CNN
F 3 "" H 1400 1650 50  0001 C CNN
	1    1400 1650
	1    0    0    -1  
$EndComp
Wire Wire Line
	1250 1500 1250 1600
Wire Wire Line
	2150 1600 2150 1500
Wire Wire Line
	1400 1650 1400 1600
$Comp
L power:GNDREF #PWR0106
U 1 1 5E459850
P 3150 2650
F 0 "#PWR0106" H 3150 2400 50  0001 C CNN
F 1 "GNDREF" H 3155 2477 50  0000 C CNN
F 2 "" H 3150 2650 50  0001 C CNN
F 3 "" H 3150 2650 50  0001 C CNN
	1    3150 2650
	1    0    0    -1  
$EndComp
Wire Wire Line
	4050 2750 3850 2750
Wire Wire Line
	3550 2750 3400 2750
$Comp
L Device:C C9
U 1 1 5E45FA51
P 1250 3000
F 0 "C9" H 1365 3046 50  0000 L CNN
F 1 "0.1uF" H 1365 2955 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 1288 2850 50  0001 C CNN
F 3 "~" H 1250 3000 50  0001 C CNN
	1    1250 3000
	1    0    0    -1  
$EndComp
Wire Wire Line
	1250 2850 1250 2800
$Comp
L power:GNDREF #PWR0107
U 1 1 5E462639
P 1250 3300
F 0 "#PWR0107" H 1250 3050 50  0001 C CNN
F 1 "GNDREF" H 1255 3127 50  0000 C CNN
F 2 "" H 1250 3300 50  0001 C CNN
F 3 "" H 1250 3300 50  0001 C CNN
	1    1250 3300
	1    0    0    -1  
$EndComp
Wire Wire Line
	1250 3150 1250 3300
Wire Wire Line
	4050 2450 1600 2450
Wire Wire Line
	1600 2450 1600 2800
Wire Wire Line
	1600 2800 1250 2800
Connection ~ 1250 2800
Wire Wire Line
	1250 2800 1250 2650
$Comp
L power:+3V3 #PWR0108
U 1 1 5E47183D
P 1250 2300
F 0 "#PWR0108" H 1250 2150 50  0001 C CNN
F 1 "+3V3" H 1265 2473 50  0000 C CNN
F 2 "" H 1250 2300 50  0001 C CNN
F 3 "" H 1250 2300 50  0001 C CNN
	1    1250 2300
	1    0    0    -1  
$EndComp
Wire Wire Line
	1250 2350 1250 2300
$Comp
L Device:C C10
U 1 1 5E476C74
P 2600 1350
F 0 "C10" H 2715 1396 50  0000 L CNN
F 1 "0.1uF" H 2715 1305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 2638 1200 50  0001 C CNN
F 3 "~" H 2600 1350 50  0001 C CNN
	1    2600 1350
	1    0    0    -1  
$EndComp
$Comp
L Device:C C11
U 1 1 5E476C7A
P 3050 1350
F 0 "C11" H 3165 1396 50  0000 L CNN
F 1 "0.1uF" H 3165 1305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 3088 1200 50  0001 C CNN
F 3 "~" H 3050 1350 50  0001 C CNN
	1    3050 1350
	1    0    0    -1  
$EndComp
$Comp
L Device:C C12
U 1 1 5E476C80
P 3500 1350
F 0 "C12" H 3615 1396 50  0000 L CNN
F 1 "4.7uF" H 3615 1305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 3538 1200 50  0001 C CNN
F 3 "~" H 3500 1350 50  0001 C CNN
	1    3500 1350
	1    0    0    -1  
$EndComp
Wire Wire Line
	2600 1200 2600 1000
Wire Wire Line
	3050 1200 3050 1000
Wire Wire Line
	3500 1200 3500 1000
Wire Wire Line
	3500 1600 3500 1500
Wire Wire Line
	2600 1500 2600 1600
$Comp
L power:GNDREF #PWR0109
U 1 1 5E47EF33
P 3050 1650
F 0 "#PWR0109" H 3050 1400 50  0001 C CNN
F 1 "GNDREF" H 3055 1477 50  0000 C CNN
F 2 "" H 3050 1650 50  0001 C CNN
F 3 "" H 3050 1650 50  0001 C CNN
	1    3050 1650
	1    0    0    -1  
$EndComp
Wire Wire Line
	5150 1000 5350 1000
Wire Wire Line
	5450 1000 5450 1350
Connection ~ 5150 1000
Wire Wire Line
	5350 1350 5350 1000
Connection ~ 5350 1000
Wire Wire Line
	5350 1000 5450 1000
Wire Wire Line
	5450 1000 5450 850 
Connection ~ 5450 1000
$Comp
L power:+3V3 #PWR0110
U 1 1 5E488EAA
P 5450 850
F 0 "#PWR0110" H 5450 700 50  0001 C CNN
F 1 "+3V3" H 5465 1023 50  0000 C CNN
F 2 "" H 5450 850 50  0001 C CNN
F 3 "" H 5450 850 50  0001 C CNN
	1    5450 850 
	1    0    0    -1  
$EndComp
$Comp
L Power_Management:MIC2026-1BM U2
U 1 1 5E48C83E
P 7600 2250
F 0 "U2" H 7600 2817 50  0000 C CNN
F 1 "MIC2026-1BM" H 7600 2726 50  0000 C CNN
F 2 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" H 7600 2250 50  0001 C CNN
F 3 "http://ww1.microchip.com/downloads/en/DeviceDoc/mic2026.pdf" H 7600 2250 50  0001 C CNN
	1    7600 2250
	1    0    0    -1  
$EndComp
$Comp
L Power_Management:MIC2026-1BM U3
U 1 1 5E4980AF
P 7600 3600
F 0 "U3" H 7600 4167 50  0000 C CNN
F 1 "MIC2026-1BM" H 7600 4076 50  0000 C CNN
F 2 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" H 7600 3600 50  0001 C CNN
F 3 "http://ww1.microchip.com/downloads/en/DeviceDoc/mic2026.pdf" H 7600 3600 50  0001 C CNN
	1    7600 3600
	1    0    0    -1  
$EndComp
Wire Wire Line
	6250 2650 6900 2650
Wire Wire Line
	6900 2650 6900 2250
Wire Wire Line
	6900 2250 7200 2250
Wire Wire Line
	6250 3150 6750 3150
Wire Wire Line
	6750 3150 6750 3300
Wire Wire Line
	6750 3300 7200 3300
Wire Wire Line
	6250 3650 6750 3650
Wire Wire Line
	6750 3650 6750 3600
Wire Wire Line
	6750 3600 7200 3600
Wire Wire Line
	6800 2250 6250 2250
Wire Wire Line
	6250 3750 6800 3750
Wire Wire Line
	6800 3750 6800 3700
Wire Wire Line
	6800 3700 7200 3700
Wire Wire Line
	7200 3400 6650 3400
Wire Wire Line
	6650 3400 6650 3250
Wire Wire Line
	6650 3250 6250 3250
Wire Wire Line
	6250 2750 7000 2750
Wire Wire Line
	7000 2750 7000 2350
Wire Wire Line
	7000 2350 7200 2350
$Comp
L power:+5V #PWR0111
U 1 1 5E4B004D
P 8100 1800
F 0 "#PWR0111" H 8100 1650 50  0001 C CNN
F 1 "+5V" H 8115 1973 50  0000 C CNN
F 2 "" H 8100 1800 50  0001 C CNN
F 3 "" H 8100 1800 50  0001 C CNN
	1    8100 1800
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR0112
U 1 1 5E4B2D6F
P 8100 3150
F 0 "#PWR0112" H 8100 3000 50  0001 C CNN
F 1 "+5V" H 8115 3323 50  0000 C CNN
F 2 "" H 8100 3150 50  0001 C CNN
F 3 "" H 8100 3150 50  0001 C CNN
	1    8100 3150
	1    0    0    -1  
$EndComp
Wire Wire Line
	8000 1950 8100 1950
Wire Wire Line
	8100 1950 8100 1800
Wire Wire Line
	8000 3300 8100 3300
Wire Wire Line
	8100 3300 8100 3150
$Comp
L power:GNDREF #PWR0113
U 1 1 5E4BC598
P 7600 2800
F 0 "#PWR0113" H 7600 2550 50  0001 C CNN
F 1 "GNDREF" H 7605 2627 50  0000 C CNN
F 2 "" H 7600 2800 50  0001 C CNN
F 3 "" H 7600 2800 50  0001 C CNN
	1    7600 2800
	1    0    0    -1  
$EndComp
Wire Wire Line
	7600 2800 7600 2750
$Comp
L power:GNDREF #PWR0114
U 1 1 5E4BF4B7
P 7600 4150
F 0 "#PWR0114" H 7600 3900 50  0001 C CNN
F 1 "GNDREF" H 7605 3977 50  0000 C CNN
F 2 "" H 7600 4150 50  0001 C CNN
F 3 "" H 7600 4150 50  0001 C CNN
	1    7600 4150
	1    0    0    -1  
$EndComp
Wire Wire Line
	7600 4150 7600 4100
Text HLabel 6350 3550 2    50   Input ~ 0
USB_DP_DN4
Text HLabel 6350 2450 2    50   Input ~ 0
USB_DM_DN2
Text HLabel 6350 2950 2    50   Input ~ 0
USB_DM_DN3
Text HLabel 6350 3450 2    50   Input ~ 0
USB_DM_DN4
Text HLabel 6350 3050 2    50   Input ~ 0
USB_DP_DN3
Text HLabel 6350 2550 2    50   Input ~ 0
USB_DP_DN2
Text HLabel 6350 2050 2    50   Input ~ 0
USB_DP_DN1
Text HLabel 6350 1950 2    50   Input ~ 0
USB_DM_DN1
Wire Wire Line
	6350 3450 6250 3450
Wire Wire Line
	6350 3550 6250 3550
Wire Wire Line
	6350 2950 6250 2950
Wire Wire Line
	6350 3050 6250 3050
Wire Wire Line
	6350 2550 6250 2550
Wire Wire Line
	6250 2450 6350 2450
Wire Wire Line
	6250 1950 6350 1950
Wire Wire Line
	6250 2050 6350 2050
Wire Wire Line
	6250 2150 6950 2150
Wire Wire Line
	6950 2150 6950 1950
Wire Wire Line
	6950 1950 7200 1950
Wire Wire Line
	6800 2250 6800 2200
Wire Wire Line
	6800 2200 7050 2200
Wire Wire Line
	7050 2200 7050 2050
Wire Wire Line
	7050 2050 7200 2050
Text HLabel 8100 2150 2    50   Input ~ 0
PRT_PWR_1
Text HLabel 8100 2350 2    50   Input ~ 0
PRT_PWR_2
Text HLabel 8100 3500 2    50   Input ~ 0
PRT_PWR_3
Text HLabel 8100 3700 2    50   Input ~ 0
PRT_PWR_4
Wire Wire Line
	8000 2150 8100 2150
Wire Wire Line
	8000 2350 8100 2350
Wire Wire Line
	8000 3500 8100 3500
Wire Wire Line
	8100 3700 8000 3700
Text HLabel 7600 950  0    50   Input ~ 0
BOARD_5V
Text HLabel 7600 1150 0    50   Input ~ 0
BOARD_3V3
$Comp
L power:+5V #PWR0115
U 1 1 5E5C04C3
P 7750 850
F 0 "#PWR0115" H 7750 700 50  0001 C CNN
F 1 "+5V" H 7765 1023 50  0000 C CNN
F 2 "" H 7750 850 50  0001 C CNN
F 3 "" H 7750 850 50  0001 C CNN
	1    7750 850 
	1    0    0    -1  
$EndComp
$Comp
L power:+3V3 #PWR0116
U 1 1 5E5C0811
P 7850 1050
F 0 "#PWR0116" H 7850 900 50  0001 C CNN
F 1 "+3V3" H 7865 1223 50  0000 C CNN
F 2 "" H 7850 1050 50  0001 C CNN
F 3 "" H 7850 1050 50  0001 C CNN
	1    7850 1050
	1    0    0    -1  
$EndComp
Wire Wire Line
	7750 850  7750 950 
Wire Wire Line
	7750 950  7600 950 
Wire Wire Line
	7600 1150 7850 1150
Wire Wire Line
	7850 1150 7850 1050
Text HLabel 7600 1350 0    50   Input ~ 0
BOARD_GND
$Comp
L power:GNDREF #PWR0117
U 1 1 5E60C9CA
P 7750 1400
F 0 "#PWR0117" H 7750 1150 50  0001 C CNN
F 1 "GNDREF" H 7755 1227 50  0000 C CNN
F 2 "" H 7750 1400 50  0001 C CNN
F 3 "" H 7750 1400 50  0001 C CNN
	1    7750 1400
	1    0    0    -1  
$EndComp
Wire Wire Line
	7750 1400 7750 1350
Wire Wire Line
	7600 1350 7750 1350
Wire Wire Line
	4050 2550 3400 2550
Wire Wire Line
	3400 2550 3400 2650
$Comp
L power:GNDREF #PWR0118
U 1 1 5E6B4FA3
P 3150 4100
F 0 "#PWR0118" H 3150 3850 50  0001 C CNN
F 1 "GNDREF" H 3155 3927 50  0000 C CNN
F 2 "" H 3150 4100 50  0001 C CNN
F 3 "" H 3150 4100 50  0001 C CNN
	1    3150 4100
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R6
U 1 1 5E6C2A9C
P 3150 3900
F 0 "R6" H 3218 3946 50  0000 L CNN
F 1 "100k" H 3218 3855 50  0000 L CNN
F 2 "Resistor_SMD:R_1206_3216Metric" V 3190 3890 50  0001 C CNN
F 3 "~" H 3150 3900 50  0001 C CNN
	1    3150 3900
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R7
U 1 1 5E6C91D9
P 3500 3900
F 0 "R7" H 3568 3946 50  0000 L CNN
F 1 "100k" H 3568 3855 50  0000 L CNN
F 2 "Resistor_SMD:R_1206_3216Metric" V 3540 3890 50  0001 C CNN
F 3 "~" H 3500 3900 50  0001 C CNN
	1    3500 3900
	1    0    0    -1  
$EndComp
Connection ~ 3050 1000
Wire Wire Line
	3850 1000 3850 1950
Connection ~ 4850 1000
Connection ~ 3500 1000
Wire Wire Line
	3050 1000 3500 1000
Connection ~ 3850 1000
Wire Wire Line
	3850 1000 4850 1000
Wire Wire Line
	3850 1950 4050 1950
Wire Wire Line
	3500 1000 3850 1000
Wire Wire Line
	3050 1500 3050 1600
Connection ~ 2600 1000
Wire Wire Line
	2600 1000 3050 1000
Connection ~ 2150 1000
Wire Wire Line
	2150 1000 2600 1000
Wire Wire Line
	1700 1000 2150 1000
Wire Wire Line
	4050 2250 4000 2250
Wire Wire Line
	4000 2150 4050 2150
Text HLabel 4000 2250 0    50   Input ~ 0
USB_DP_UP
Text HLabel 4000 2150 0    50   Input ~ 0
USB_DM_UP
Connection ~ 1250 1600
Wire Wire Line
	1250 1600 1400 1600
Wire Wire Line
	800  1200 800  1000
Wire Wire Line
	800  1000 1250 1000
Wire Wire Line
	1250 1000 1700 1000
Connection ~ 1250 1000
Wire Wire Line
	1400 1600 1700 1600
Connection ~ 1400 1600
Wire Wire Line
	1700 1500 1700 1600
Connection ~ 1700 1600
Wire Wire Line
	1700 1600 2150 1600
Wire Wire Line
	800  1500 800  1600
Wire Wire Line
	800  1600 1250 1600
Wire Wire Line
	2600 1600 3050 1600
Connection ~ 3050 1600
Wire Wire Line
	3050 1600 3050 1650
Wire Wire Line
	3050 1600 3500 1600
Wire Wire Line
	5150 4600 5150 4350
$Comp
L Interface_USB:USB2514B_Bi U1
U 1 1 5E416C94
P 5150 2850
F 0 "U1" H 5937 1379 50  0000 C CNN
F 1 "USB2514B_Bi" H 5937 1288 50  0000 C CNN
F 2 "Package_DFN_QFN:QFN-36-1EP_6x6mm_P0.5mm_EP3.7x3.7mm" H 6450 1350 50  0001 C CNN
F 3 "http://ww1.microchip.com/downloads/en/DeviceDoc/00001692C.pdf" H 6750 1250 50  0001 C CNN
	1    5150 2850
	1    0    0    -1  
$EndComp
Wire Wire Line
	2700 3750 2700 3550
Wire Wire Line
	2700 3550 3600 3550
Wire Wire Line
	3600 3550 3600 3350
Wire Wire Line
	3600 3350 4050 3350
Wire Wire Line
	2200 3750 2200 3500
Wire Wire Line
	2200 3500 3400 3500
Wire Wire Line
	3400 3500 3400 3250
Wire Wire Line
	3400 3250 4050 3250
Wire Wire Line
	3150 2650 3400 2650
Connection ~ 3400 2650
Wire Wire Line
	3400 2650 3400 2750
Wire Wire Line
	3150 3650 4050 3650
Wire Wire Line
	3150 3650 3150 3750
Wire Wire Line
	3150 4050 3150 4100
Wire Wire Line
	3850 3850 4050 3850
Wire Wire Line
	3950 3950 4050 3950
Wire Wire Line
	3950 4900 3950 4800
$Comp
L power:GNDREF #PWR0121
U 1 1 5E67F0D8
P 3950 4900
F 0 "#PWR0121" H 3950 4650 50  0001 C CNN
F 1 "GNDREF" H 3955 4727 50  0000 C CNN
F 2 "" H 3950 4900 50  0001 C CNN
F 3 "" H 3950 4900 50  0001 C CNN
	1    3950 4900
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R5
U 1 1 5E66A087
P 3950 4650
F 0 "R5" H 4018 4696 50  0000 L CNN
F 1 "100k" H 4018 4605 50  0000 L CNN
F 2 "Resistor_SMD:R_1206_3216Metric" V 3990 4640 50  0001 C CNN
F 3 "~" H 3950 4650 50  0001 C CNN
	1    3950 4650
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R2
U 1 1 5E458B0F
P 3700 2750
F 0 "R2" V 3810 2750 50  0000 C CNN
F 1 "12k" V 3586 2750 50  0000 C CNN
F 2 "Resistor_SMD:R_1206_3216Metric" V 3740 2740 50  0001 C CNN
F 3 "~" H 3700 2750 50  0001 C CNN
	1    3700 2750
	0    1    1    0   
$EndComp
$Comp
L Device:R_US R3
U 1 1 5E462633
P 1250 2500
F 0 "R3" H 1318 2546 50  0000 L CNN
F 1 "100k" H 1318 2455 50  0000 L CNN
F 2 "Resistor_SMD:R_1206_3216Metric" V 1290 2490 50  0001 C CNN
F 3 "~" H 1250 2500 50  0001 C CNN
	1    1250 2500
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R4
U 1 1 5E5E7009
P 3500 4650
F 0 "R4" H 3568 4696 50  0000 L CNN
F 1 "100k" H 3568 4605 50  0000 L CNN
F 2 "Resistor_SMD:R_1206_3216Metric" V 3540 4640 50  0001 C CNN
F 3 "~" H 3500 4650 50  0001 C CNN
	1    3500 4650
	1    0    0    -1  
$EndComp
Wire Wire Line
	3950 3950 3950 4500
Wire Wire Line
	3500 3750 4050 3750
Wire Wire Line
	3850 3850 3850 4450
Wire Wire Line
	3850 4450 3500 4450
Wire Wire Line
	3500 4450 3500 4500
$Comp
L power:GNDREF #PWR0145
U 1 1 5E5C69A8
P 3500 4100
F 0 "#PWR0145" H 3500 3850 50  0001 C CNN
F 1 "GNDREF" H 3505 3927 50  0000 C CNN
F 2 "" H 3500 4100 50  0001 C CNN
F 3 "" H 3500 4100 50  0001 C CNN
	1    3500 4100
	1    0    0    -1  
$EndComp
$Comp
L power:GNDREF #PWR0146
U 1 1 5E5C6D8B
P 3500 4900
F 0 "#PWR0146" H 3500 4650 50  0001 C CNN
F 1 "GNDREF" H 3505 4727 50  0000 C CNN
F 2 "" H 3500 4900 50  0001 C CNN
F 3 "" H 3500 4900 50  0001 C CNN
	1    3500 4900
	1    0    0    -1  
$EndComp
Wire Wire Line
	3500 4050 3500 4100
Wire Wire Line
	3500 4800 3500 4900
$EndSCHEMATC
