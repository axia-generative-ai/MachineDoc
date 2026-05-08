# v1 retrieval review (same eval set as v2)


**Top-1**: 3/25 (12%)  |  **Top-3**: 4/25 (16%)

## ✗ `v2_001` (2193ms)
- query: How do I fix ABB robot error 10009?
- expected: `abb_irb_troubleshooting` p81-81
- top-3:
    1. [vector dist=0.284] abb_irb_troubleshooting p291
    2. [vector dist=0.284] abb_irb_troubleshooting p325
    3. [vector dist=0.285] abb_irb_troubleshooting p47

## ✓ `v2_002` (104ms)
- query: ABB robot error 20184, what should I do?
- expected: `abb_irb_troubleshooting` p115-115
- top-3:
    1. [vector dist=0.280] abb_irb_troubleshooting p93
    2. [vector dist=0.283] abb_irb_troubleshooting p325
    3. [vector dist=0.285] abb_irb_troubleshooting p114  ✓

## ✗ `v2_003` (105ms)
- query: ABB robot error 20506, what should I do?
- expected: `abb_irb_troubleshooting` p139-139
- top-3:
    1. [vector dist=0.277] abb_irb_troubleshooting p325
    2. [vector dist=0.295] abb_irb_troubleshooting p291
    3. [vector dist=0.295] abb_irb_troubleshooting p147

## ✗ `v2_004` (127ms)
- query: ABB robot error 37044, what should I do?
- expected: `abb_irb_troubleshooting` p161-161
- top-3:
    1. [vector dist=0.251] abb_irb_troubleshooting p325
    2. [vector dist=0.287] abb_irb_troubleshooting p147
    3. [vector dist=0.288] abb_irb_troubleshooting p325

## ✗ `v2_005` (112ms)
- query: ABB robot error 40074, what should I do?
- expected: `abb_irb_troubleshooting` p196-197
- top-3:
    1. [vector dist=0.267] abb_irb_troubleshooting p325
    2. [vector dist=0.286] abb_irb_troubleshooting p114
    3. [vector dist=0.286] abb_irb_troubleshooting p147

## ✗ `v2_006` (106ms)
- query: How do I fix ABB robot error 40196?
- expected: `abb_irb_troubleshooting` p206-206
- top-3:
    1. [vector dist=0.267] abb_irb_troubleshooting p325
    2. [vector dist=0.275] abb_irb_troubleshooting p52
    3. [vector dist=0.277] abb_irb_troubleshooting p291

## ✗ `v2_007` (103ms)
- query: Troubleshooting steps for ABB error 40721
- expected: `abb_irb_troubleshooting` p231-231
- top-3:
    1. [vector dist=0.344] fanuc_series0m_maintenance p425
    2. [vector dist=0.344] yaskawa_ga700_technical p929
    3. [vector dist=0.355] abb_irb_troubleshooting p135

## ✗ `v2_008` (125ms)
- query: Troubleshooting steps for ABB error 41508
- expected: `abb_irb_troubleshooting` p253-253
- top-3:
    1. [vector dist=0.348] mitsubishi_servo_amp_instruction p29
    2. [vector dist=0.372] abb_irb_troubleshooting p259
    3. [vector dist=0.376] abb_irb_troubleshooting p95

## ✗ `v2_009` (119ms)
- query: Troubleshooting steps for ABB error 41721
- expected: `abb_irb_troubleshooting` p277-277
- top-3:
    1. [vector dist=0.356] abb_irb_troubleshooting p95
    2. [vector dist=0.363] mitsubishi_servo_amp_instruction p29
    3. [vector dist=0.363] yaskawa_ga700_technical p929

## ✗ `v2_010` (105ms)
- query: Troubleshooting steps for ABB error 71045
- expected: `abb_irb_troubleshooting` p316-316
- top-3:
    1. [vector dist=0.338] abb_irb_troubleshooting p334
    2. [vector dist=0.353] abb_irb_troubleshooting p326
    3. [vector dist=0.353] abb_irb_troubleshooting p341

## ✓ `v2_011` (222ms)
- query: Troubleshooting steps for ABB error 71340
- expected: `abb_irb_troubleshooting` p331-331
- top-3:
    1. [vector dist=0.303] abb_irb_troubleshooting p326  ✓
    2. [vector dist=0.324] abb_irb_troubleshooting p334
    3. [vector dist=0.325] abb_irb_troubleshooting p341

## ✗ `v2_012` (100ms)
- query: What does ABB IRB error 110634 mean?
- expected: `abb_irb_troubleshooting` p370-370
- top-3:
    1. [vector dist=0.278] yaskawa_ga700_technical p261
    2. [vector dist=0.288] fanuc_series0m_maintenance p470
    3. [vector dist=0.289] yaskawa_ga700_technical p551

## ✗ `v2_013` (125ms)
- query: How do I fix ABB robot error 110713?
- expected: `abb_irb_troubleshooting` p378-378
- top-3:
    1. [vector dist=0.273] abb_irb_troubleshooting p47
    2. [vector dist=0.273] abb_irb_troubleshooting p364
    3. [vector dist=0.275] abb_irb_troubleshooting p325

## ✗ `v2_014` (235ms)
- query: Troubleshooting steps for ABB error 111801
- expected: `abb_irb_troubleshooting` p397-397
- top-3:
    1. [vector dist=0.337] abb_irb_troubleshooting p95
    2. [vector dist=0.344] abb_irb_troubleshooting p388
    3. [vector dist=0.358] abb_irb_troubleshooting p95

## ✗ `v2_015` (113ms)
- query: Troubleshooting steps for ABB error 112434
- expected: `abb_irb_troubleshooting` p420-420
- top-3:
    1. [vector dist=0.345] yaskawa_ga700_technical p261
    2. [vector dist=0.351] fanuc_series0m_maintenance p425
    3. [vector dist=0.352] abb_irb_troubleshooting p364

## ✗ `v2_016` (106ms)
- query: What does ABB IRB error 134134 mean?
- expected: `abb_irb_troubleshooting` p453-454
- top-3:
    1. [vector dist=0.296] yaskawa_ga700_technical p551
    2. [vector dist=0.306] yaskawa_ga700_technical p261
    3. [vector dist=0.313] fanuc_series0m_maintenance p18

## ✗ `v2_017` (127ms)
- query: Fanuc Series 0 alarm SV5197, recommended action?
- expected: `fanuc_series0m_maintenance` p406-406
- top-3:
    1. [vector dist=0.284] mitsubishi_servo_amp_instruction p8
    2. [vector dist=0.297] fanuc_series0m_maintenance p56
    3. [vector dist=0.310] fanuc_series0m_maintenance p498

## ✗ `v2_018` (97ms)
- query: How do I clear Fanuc CNC alarm DS1450?
- expected: `fanuc_series0m_maintenance` p487-491
- top-3:
    1. [vector dist=0.293] fanuc_series0m_maintenance p392
    2. [vector dist=0.295] fanuc_series0m_maintenance p56
    3. [vector dist=0.295] fanuc_series0m_maintenance p560

## ✗ `v2_019` (120ms)
- query: What does LS S100 RAPIEnet parameter COM-12 configure?
- expected: `ls_s100_rapienet_user` p14-14
- top-3:
    1. [vector dist=0.280] schneider_atv320_programming p290
    2. [vector dist=0.286] yaskawa_ga700_technical p591
    3. [vector dist=0.292] yaskawa_ga700_technical p697

## ✗ `v2_020` (117ms)
- query: Mitsubishi servo amp alarm A.47 — cause and remedy?
- expected: `mitsubishi_servo_amp_instruction` p151-151
- top-3:
    1. [vector dist=0.212] mitsubishi_servo_amp_instruction p105
    2. [vector dist=0.216] mitsubishi_servo_amp_instruction p30
    3. [vector dist=0.218] fanuc_series0m_maintenance p350

## ✗ `v2_021` (102ms)
- query: Allen-Bradley drive code F073, what to do?
- expected: `rockwell_powerflex520_user` p162-162
- top-3:
    1. [vector dist=0.242] schneider_atv320_programming p75
    2. [vector dist=0.275] rockwell_powerflex520_user p14
    3. [vector dist=0.278] schneider_atv320_programming p300

## ✗ `v2_022` (102ms)
- query: Schneider ATV320 fault OLF — cause?
- expected: `schneider_atv320_programming` p50-50
- top-3:
    1. [vector dist=0.257] yaskawa_ga700_technical p277
    2. [vector dist=0.278] rockwell_powerflex520_user p236
    3. [vector dist=0.285] yaskawa_ga700_technical p728

## ✓ `v2_023` (99ms)
- query: Siemens S7 diagnostics — code 1200 meaning?
- expected: `siemens_s7_diagnostics` p1-2
- top-3:
    1. [vector dist=0.308] siemens_s7_diagnostics p3  ✓
    2. [vector dist=0.311] siemens_s7_diagnostics p5
    3. [vector dist=0.329] siemens_s7_diagnostics p25

## ✓ `v2_024` (108ms)
- query: Yaskawa GA700 fault rr — meaning?
- expected: `yaskawa_ga700_technical` p243-243
- top-3:
    1. [vector dist=0.322] yaskawa_ga700_technical p728  ✓
    2. [vector dist=0.324] ls_s100_rapienet_user p46
    3. [vector dist=0.331] yaskawa_ga700_technical p855

## ✗ `v2_025` (99ms)
- query: GA700 drive alarm Er-21, what to do?
- expected: `yaskawa_ga700_technical` p269-269
- top-3:
    1. [vector dist=0.304] mitsubishi_servo_amp_instruction p8
    2. [vector dist=0.306] mitsubishi_servo_amp_instruction p159
    3. [vector dist=0.309] schneider_atv320_programming p74
