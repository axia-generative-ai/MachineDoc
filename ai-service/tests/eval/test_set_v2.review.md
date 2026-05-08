# v2 candidate eval review

Cases: 25  |  Top-3 manual+page check below


**Top-1**: 15/25 (60%)  |  **Top-3**: 23/25 (92%)

## ✓ `v2_001` — error_code  (2823ms)
- **query**: How do I fix ABB robot error 10009?
- **expected**: `abb_irb_troubleshooting` p81-81 (procedure) — 10009, Work memory full
- **snippet**: `10009, Work memory full
The task arg has no memory left for new RAPID instructions or data.
Save the program and then restart the system.`
- **top-3**:
    1. [rerank 0.259] abb_irb_troubleshooting p47 — Info/Illustration
    2. [rerank 0.136] abb_irb_troubleshooting p81 — 10009, Work memory full  ✓
    3. [rerank 0.049] abb_irb_troubleshooting p13 — 1.2. Safety symbols on the manipulator labels / Lifting of robot

## ✗ `v2_002` — error_code  (627ms)
- **query**: ABB robot error 20184, what should I do?
- **expected**: `abb_irb_troubleshooting` p115-115 (procedure) — 20184, Incorrect argument for System Inputs
- **snippet**: `20184, Incorrect argument for System Inputs
An undefined Start Mode has been
declared for System IO.`
- **top-3**:
    1. [rerank 0.129] abb_irb_troubleshooting p427 — 118807, Internal execution error
    2. [rerank 0.020] abb_irb_troubleshooting p47 — Info/Illustration
    3. [rerank 0.014] abb_irb_troubleshooting p54 — Such errors may occur anywhere in the robot system and may be due to:

## ✓ `v2_003` — error_code  (899ms)
- **query**: ABB robot error 20506, what should I do?
- **expected**: `abb_irb_troubleshooting` p139-139 (procedure) — 20506, Test Stop open
- **snippet**: `20506, Test Stop open
The Test Mode Safeguarded Stop circuit has been broken.`
- **top-3**:
    1. [rerank 0.164] abb_irb_troubleshooting p427 — 118807, Internal execution error
    2. [rerank 0.115] abb_irb_troubleshooting p139 — 20506, Test Stop open  ✓
    3. [rerank 0.025] abb_irb_troubleshooting p47 — Info/Illustration

## ✓ `v2_004` — error_code  (547ms)
- **query**: ABB robot error 37044, what should I do?
- **expected**: `abb_irb_troubleshooting` p161-161 (procedure) — 37044, Overload on Panel Board digital output
- **snippet**: `37044, Overload on Panel Board digital output`
- **top-3**:
    1. [rerank 0.093] abb_irb_troubleshooting p161 — 37044, Overload on Panel Board digital output  ✓
    2. [rerank 0.091] abb_irb_troubleshooting p427 — 118807, Internal execution error
    3. [rerank 0.060] abb_irb_troubleshooting p26 — during trouble shooting the robot system.

## ✓ `v2_005` — error_code  (871ms)
- **query**: ABB robot error 40074, what should I do?
- **expected**: `abb_irb_troubleshooting` p196-197 (procedure) — 40074, Reference error
- **snippet**: `40074, Reference error
arg
not entire data reference
The specified name identifies an object
other than data. Check if the desired
195
data is hidden by some ot`
- **top-3**:
    1. [rerank 0.108] abb_irb_troubleshooting p427 — 118807, Internal execution error
    2. [rerank 0.061] abb_irb_troubleshooting p26 — during trouble shooting the robot system.
    3. [rerank 0.027] abb_irb_troubleshooting p196 — 40074, Reference error  ✓

## ✓ `v2_006` — error_code  (977ms)
- **query**: How do I fix ABB robot error 40196?
- **expected**: `abb_irb_troubleshooting` p206-206 (procedure) — 40196, Instruction error
- **snippet**: `40196, Instruction error
Task arg: Attempt to
execute place holder
Remove the place holder or the
instruction containing it, or make the
instruction complete. T`
- **top-3**:
    1. [rerank 0.357] abb_irb_troubleshooting p206 — 40196, Instruction error  ✓
    2. [rerank 0.342] abb_irb_troubleshooting p47 — Info/Illustration
    3. [rerank 0.032] abb_irb_troubleshooting p427 — 118807, Internal execution error

## ✓ `v2_007` — error_code  (526ms)
- **query**: Troubleshooting steps for ABB error 40721
- **expected**: `abb_irb_troubleshooting` p231-231 (procedure) — 40721, IO Installation
- **snippet**: `40721, IO Installation
Task arg:
The system could not refresh all IO signals as RAPID symbols.`
- **top-3**:
    1. [rerank 0.276] abb_irb_troubleshooting p192 — 40021, Instruction error
    2. [rerank 0.072] abb_irb_troubleshooting p231 — 40721, IO Installation  ✓
    3. [rerank 0.053] abb_irb_troubleshooting p26 — Each fault or error is first detected as a symptom, for which an error event log message

## ✓ `v2_008` — error_code  (480ms)
- **query**: Troubleshooting steps for ABB error 41508
- **expected**: `abb_irb_troubleshooting` p253-253 (procedure) — 41508, LoadId Error
- **snippet**: `41508, LoadId Error
Task: arg
Load Identification is not available for this robot type.
Program Ref. arg
Check next Event Log message, for the next user action `
- **top-3**:
    1. [rerank 0.091] abb_irb_troubleshooting p253 — 41508, LoadId Error  ✓
    2. [rerank 0.027] abb_irb_troubleshooting p26 — Each fault or error is first detected as a symptom, for which an error event log message
    3. [rerank 0.009] abb_irb_troubleshooting p222 — 40590, ParId error

## ✓ `v2_009` — error_code  (666ms)
- **query**: Troubleshooting steps for ABB error 41721
- **expected**: `abb_irb_troubleshooting` p277-277 (procedure) — 41721, Invalid Argument
- **snippet**: `41721, Invalid Argument
Task: arg
The type arg in argument arg is invalid.
Program Ref: arg
Change the type to a valid one (arg).`
- **top-3**:
    1. [rerank 0.503] abb_irb_troubleshooting p192 — 40021, Instruction error
    2. [rerank 0.093] abb_irb_troubleshooting p277 — 41721, Invalid Argument  ✓
    3. [rerank 0.037] abb_irb_troubleshooting p26 — Each fault or error is first detected as a symptom, for which an error event log message

## ✓ `v2_010` — error_code  (411ms)
- **query**: Troubleshooting steps for ABB error 71045
- **expected**: `abb_irb_troubleshooting` p316-316 (procedure) — 71045, Invalid filter specification
- **snippet**: `71045, Invalid filter specification
The I/O configuration for I/O signal <arg> is invalid.
No filter times can be specified for this type of I/O signal.
This I/`
- **top-3**:
    1. [rerank 0.087] abb_irb_troubleshooting p327 — 71306, DeviceNet unknown error
    2. [rerank 0.057] abb_irb_troubleshooting p316 — 71045, Invalid filter specification  ✓
    3. [rerank 0.026] abb_irb_troubleshooting p26 — Each fault or error is first detected as a symptom, for which an error event log message

## ✓ `v2_011` — error_code  (589ms)
- **query**: Troubleshooting steps for ABB error 71340
- **expected**: `abb_irb_troubleshooting` p331-331 (procedure) — 71340, Invalid I/O unit
- **snippet**: `71340, Invalid I/O unit
The I/O configuration is invalid.
One of the fieldbus commands has a reference to an invalid/unknown
I/O unit <arg>.
All fieldbus comman`
- **top-3**:
    1. [rerank 0.100] abb_irb_troubleshooting p327 — 71306, DeviceNet unknown error  ✓
    2. [rerank 0.026] abb_irb_troubleshooting p331 — 71340, Invalid I/O unit
    3. [rerank 0.017] abb_irb_troubleshooting p26 — Each fault or error is first detected as a symptom, for which an error event log message

## ✓ `v2_012` — error_code  (723ms)
- **query**: What does ABB IRB error 110634 mean?
- **expected**: `abb_irb_troubleshooting` p370-370 (procedure) — 110634, Spot application cfg data limit error
- **snippet**: `110634, Spot application cfg data limit error
Task: arg
The data value is outside the limit.
Change the value.`
- **top-3**:
    1. [rerank 0.069] abb_irb_troubleshooting p370 — 110634, Spot application cfg data limit error  ✓
    2. [rerank 0.004] abb_irb_troubleshooting p327 — 71306, DeviceNet unknown error
    3. [rerank 0.000] abb_irb_troubleshooting p452 — 134102, Unrecoverable CBS error.

## ✓ `v2_013` — error_code  (926ms)
- **query**: How do I fix ABB robot error 110713?
- **expected**: `abb_irb_troubleshooting` p378-378 (procedure) — 110713, No current, weld 1 to 3.
- **snippet**: `110713, No current, weld 1 to 3.
Task:arg
arg
Electrodes not closed - no electrical contact at the point to be welded -
contamination of sheets - use of sealant`
- **top-3**:
    1. [rerank 0.243] abb_irb_troubleshooting p47 — Info/Illustration
    2. [rerank 0.225] abb_irb_troubleshooting p378 — 110713, No current, weld 1 to 3.  ✓
    3. [rerank 0.137] abb_irb_troubleshooting p29 — How to file a complete error report to your local ABB service personnel is detailed in section

## ✓ `v2_014` — error_code  (849ms)
- **query**: Troubleshooting steps for ABB error 111801
- **expected**: `abb_irb_troubleshooting` p397-397 (procedure) — 111801, Illegal Schedule Number
- **snippet**: `111801, Illegal Schedule Number
Task:arg
Context: arg
arg is not a valid schedule number.
Arcitune only allows schedules 1 to 99.`
- **top-3**:
    1. [rerank 0.043] abb_irb_troubleshooting p397 — 111801, Illegal Schedule Number  ✓
    2. [rerank 0.039] abb_irb_troubleshooting p26 — Each fault or error is first detected as a symptom, for which an error event log message
    3. [rerank 0.002] abb_irb_troubleshooting p95 — 11121, Backup error

## ✓ `v2_015` — error_code  (470ms)
- **query**: Troubleshooting steps for ABB error 112434
- **expected**: `abb_irb_troubleshooting` p420-420 (procedure) — 112434, Incompatible weld data format
- **snippet**: `112434, Incompatible weld data format
I/O unit: arg
Error code: arg
Internal unit: arg`
- **top-3**:
    1. [rerank 0.428] abb_irb_troubleshooting p420 — 112434, Incompatible weld data format  ✓
    2. [rerank 0.028] abb_irb_troubleshooting p26 — Each fault or error is first detected as a symptom, for which an error event log message
    3. [rerank 0.001] abb_irb_troubleshooting p101 — 12138, Restore error

## ✓ `v2_016` — error_code  (572ms)
- **query**: What does ABB IRB error 134134 mean?
- **expected**: `abb_irb_troubleshooting` p453-454 (procedure) — 134134, Gripper open failed.
- **snippet**: `134134, Gripper open failed.
Timeout while waiting for sensor feedback.
452
Check that gripper sensors are working.`
- **top-3**:
    1. [rerank 0.198] abb_irb_troubleshooting p453 — 134134, Gripper open failed.  ✓
    2. [rerank 0.017] abb_irb_troubleshooting p454 — 134145, Vacuum check error.
    3. [rerank 0.012] abb_irb_troubleshooting p449 — 134011, Subscriber unknown error

## ✓ `v2_017` — error_code  (754ms)
- **query**: Fanuc Series 0 alarm SV5197, recommended action?
- **expected**: `fanuc_series0m_maintenance` p406-406 (narrative) — Causes and Countermeasures
- **snippet**: `Causes and Countermeasures
These alarms are issued due to a failure in the optical cable, axis card, or a slave such as a servo amplifier
connected to the FSSB.`
- **top-3**:
    1. [rerank 0.552] fanuc_series0m_maintenance p406 — ALARM SV5197 (FSSB: OPEN TIME OUT)  ✓
    2. [rerank 0.280] fanuc_series0m_maintenance p406 — Causes and Countermeasures
    3. [rerank 0.010] fanuc_series0m_maintenance p34 — Details of serial Pulsecoder / #0  OFA Overflow alarm

## ✓ `v2_018` — error_code  (472ms)
- **query**: How do I clear Fanuc CNC alarm DS1450?
- **expected**: `fanuc_series0m_maintenance` p487-491 (narrative) — APPENDIX / (11) Other alarms (DS alarm)
- **snippet**: `(11) Other alarms (DS alarm)
Number
Message
Description
DS0001
SYNC EXCESS ERROR (POS DEV)
In feed axis control , the difference in the amount of
positional dev`
- **top-3**:
    1. [rerank 0.062] fanuc_series0m_maintenance p487 — APPENDIX / (11) Other alarms (DS alarm)  ✓
    2. [rerank 0.015] fanuc_series0m_maintenance p487 — APPENDIX / (11) Other alarms (DS alarm)
    3. [rerank 0.011] fanuc_series0m_maintenance p420 — 10.25.4 System Alarms 114 to 137 (Alarms on the FSSB) / Causes

## ✓ `v2_019` — error_code  (604ms)
- **query**: What does LS S100 RAPIEnet parameter COM-12 configure?
- **expected**: `ls_s100_rapienet_user` p14-14 (narrative) — communication board / Protocol
- **snippet**: `Protocol
CNF-30
*1
Option-1 Type
-
-
Displays the name of the
communication option board
installed. 'RAPIEnet+'
(Depending on the inverter OS
version, it may be`
- **top-3**:
    1. [rerank 0.503] ls_s100_rapienet_user p23 — 10.4 COM Group / ⑦ [COM-25] RAPIEnet Enable/Disable settings
    2. [rerank 0.356] ls_s100_rapienet_user p15 — communication board / Keypad parameters related to S100 RAPIEnet+ communication board  ✓
    3. [rerank 0.168] ls_s100_rapienet_user p17 — communication board / Keypad parameters for RAPIEnet+ communication board

## ✗ `v2_020` — error_code  (882ms)
- **query**: Mitsubishi servo amp alarm A.47 — cause and remedy?
- **expected**: `mitsubishi_servo_amp_instruction` p151-151 (narrative) — Alarm / Cycling the power
- **snippet**: `Cycling the power
A.10
Undervoltage


A.12
Memory error 1 (RAM)


A.15
Memory error 2 (EEP-ROM)


A.17
Board error


A.19
Memory error 3 (Flash-ROM)

`
- **top-3**:
    1. [rerank 0.447] mitsubishi_servo_amp_instruction p53 — 1 / Target
    2. [rerank 0.399] mitsubishi_servo_amp_instruction p46 — 44 / Target
    3. [rerank 0.340] mitsubishi_servo_amp_instruction p105 — When any of the following alarms has occurred, do not cycle the power of the servo amplifier repeate

## ✓ `v2_021` — error_code  (509ms)
- **query**: Allen-Bradley drive code F073, what to do?
- **expected**: `rockwell_powerflex520_user` p162-162 (narrative) — Fault Types, Descriptions, and Actions / Chapter 4          Troubleshooting
- **snippet**: `Chapter 4          Troubleshooting
F041
Phase UV Short
2
Excessive current has been
detected between these two
output terminals.
• Check the motor and drive out`
- **top-3**:
    1. [rerank 0.887] rockwell_powerflex520_user p162 — Fault Types, Descriptions, and Actions / Chapter 4          Troubleshooting  ✓
    2. [rerank 0.803] rockwell_powerflex520_user p21 — This is the safety ground for the drive that is required by code. One of these
    3. [rerank 0.408] rockwell_powerflex520_user p162 — Fault Codes / F073

## ✓ `v2_022` — error_code  (622ms)
- **query**: Schneider ATV320 fault OLF — cause?
- **expected**: `schneider_atv320_programming` p50-50 (narrative) — [Motor thermal state]
- **snippet**: `[Motor thermal state]
%
Motor thermal state.
100% = Nominal thermal state, 118% = "OLF" threshold (motor overload).`
- **top-3**:
    1. [rerank 0.308] schneider_atv320_programming p311 — Fault Codes / OLF  ✓
    2. [rerank 0.052] schneider_atv320_programming p68 — [CURRENT FAULT LIST] / [Motor overload] (OLF): Motor overload
    3. [rerank 0.052] schneider_atv320_programming p65 — [Past fault 1] / [Motor overload] (OLF): Motor overload

## ✓ `v2_023` — error_code  (390ms)
- **query**: Siemens S7 diagnostics — code 1200 meaning?
- **expected**: `siemens_s7_diagnostics` p1-2 (procedure) — TIA Portal, SIMATIC S7-1200, SIMATIC S7-1500
- **snippet**: `TIA Portal, SIMATIC S7-1200, SIMATIC S7-1500
https://support.industry.siemens.com/cs/ww/en/view/109752283
Siemens
Industry
Online
Support
Legal information
2`
- **top-3**:
    1. [rerank 0.184] siemens_s7_diagnostics p5 — Introduction  ✓
    2. [rerank 0.012] siemens_s7_diagnostics p7 — Diagnostics options
    3. [rerank 0.007] siemens_s7_diagnostics p5 — Use cases for diagnostics / System diagnostics (diagnosis of faults of electrical controller compone

## ✓ `v2_024` — error_code  (625ms)
- **query**: Yaskawa GA700 fault rr — meaning?
- **expected**: `yaskawa_ga700_technical` p243-243 (narrative) — Monitor data can only be read. / Description
- **snippet**: `Description
0020
Drive status 1
bit 0
During Run
1: During run, 0: During stop
bit 1
During Reverse
1: During reverse, 0: Forward run
bit 2
Drive ready
1: Ready`
- **top-3**:
    1. [rerank 0.308] yaskawa_ga700_technical p798 — ■4E: Braking Transistor Fault (rr) / Description  ✓
    2. [rerank 0.292] yaskawa_ga700_technical p243 — Monitor data can only be read. / Description
    3. [rerank 0.243] yaskawa_ga700_technical p728 — 11.7 F: Options / Terminal P4-PC

## ✓ `v2_025` — error_code  (953ms)
- **query**: GA700 drive alarm Er-21, what to do?
- **expected**: `yaskawa_ga700_technical` p269-269 (narrative) — 6.3 List of Fault, Minor Fault, Alarm, and Error Codes / Type
- **snippet**: `Type
Ref.
Er-08
Rated Slip Error
Flashing
Auto-Tuning Errors
317
Er-09
Acceleration Error
Flashing
Auto-Tuning Errors
317
Er-10
Motor Direction Error
Flashing
A`
- **top-3**:
    1. [rerank 0.140] yaskawa_ga700_technical p319 — 6.7 Auto-Tuning Errors / Possible Solution  ✓
    2. [rerank 0.124] yaskawa_ga700_technical p828 — It is also possible to set a motor overload alarm. Set H2-01 = 1F [Terminal M1-M2 Function Selection
    3. [rerank 0.124] yaskawa_ga700_technical p219 — It is also possible to set a motor overload alarm. Set H2-01 = 1F [Terminal M1-M2 Function Selection
