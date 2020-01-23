"""Gen. snap files on ram."""

# @formatter:off

ARR_SCLR_SNP = """
--- Start BURT header
Time:     Tue Sep 21 15:07:59 2010
Login ID: ops-cc83 (Chris Christou)
Eff  UID: 37245
Group ID: 37245
Keywords: hello world
Comments: Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4
Type:     Absolute
Directory /home/ops/burt/backupFiles
Req File: /home/ops/burt/requestFiles/SR-DI.req
--- End BURT header
SR01C-DI-COL-01:POS1 3 3.259328000000000e+00 3.259328000000000e+00 3.259328000000000e+00 % Random Inline Comment
SR01C-DI-COL-01:POS2 1 -3.276854000000000e+00
SR01C-DI-COL-02:POS1 2 -1.200000000000000e+01 -1.200000000000000e+01
SR01C-DI-COL-02:POS2 1 1.200000000000000e+01
"""

ARR_SCLR_SNP_MODS = """
--- Start BURT header
Time:     Tue Sep 21 15:07:59 2010
Login ID: ops-cc83 (Chris Christou)
Eff  UID: 37245
Group ID: 37245
Keywords: hello world
Comments: Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4
Type:     Absolute
Directory /home/ops/burt/backupFiles
Req File: /home/ops/burt/requestFiles/SR-DI.req
--- End BURT header
RON SR01C-DI-COL-01:POS1 3 3.259328000000000e+00 3.259328000000000e+00 3.259328000000000e+00 % Random Inline Comment
RO SR01C-DI-COL-01:POS2 1 -3.276854000000000e+00
WO SR01C-DI-COL-02:POS1 2 -1.200000000000000e+01 -1.200000000000000e+01
SR01C-DI-COL-02:POS2 1 1.200000000000000e+01
"""

BLANK = """
% This is a blank test file for the base case.
"""

DUPL_HEAD = """
--- Start BURT header
--- Start BURT header
--- End BURT header
--- Start BURT header
--- End BURT header
--- End BURT header
"""

ENUM = """
--- Start BURT header
Time:      time
Login ID:  user
Eff  UID:  100
Group ID:  group
Keywords:  cool,snap,file
Comments:  Hello World
Type:      Absolute
Directory: dir
Req File:  testables/req/normal.req
--- End BURT header
SR01C-DI-COL-01:ENUM 1 NIL
SR01C-DI-COL-01:ENUM2 1 "lower voltage"
SR01C-DI-COL-01:ENUM3 2 "lower voltage" "no voltage"
SR01C-DI-COL-01:ENUM4 1 "lower voltage no voltage"
"""

INLINE_COMM = """
--- Start BURT header
Time:     Tue Sep 21 15:07:59 2010
Login ID: ops-cc83 (Chris Christou)
Eff  UID: 37245
Group ID: 37245
Keywords: hello world
Comments: Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4
Type:     Absolute
Directory /home/ops/burt/backupFiles
Req File: /home/ops/burt/requestFiles/SR-DI.req
--- End BURT header
SR01C-DI-COL-01:POS1 1 3.259328000000000e+00 % Inline comments
SR01C-DI-COL-01:POS2 2 -3.276854000000000e+00 333
SR01C-DI-COL-02:POS1 1 -1.200000000000000e+01 % Inline comments % Duplicated percent % Duplicated hash 2
%%%  %%%
%SR01C-DI-COL-02:POS2 1 1.200000000000000e+01 % This PV should be ignored due to percent in front.
          %SR01C-DI-COL-02:POS2 1 1.200000000000000e+01 % Comment line with whitespace.
SR01C-DI-COL-03:POS3 1 666
"""

IOC_RESTORE_ARR = """
--- Start BURT header
Time:     Tue Sep 21 15:07:59 2010
Login ID: ops-cc83 (Chris Christou)
Eff  UID: 37245
Group ID: 37245
Keywords: hello world
Comments: Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4
Type:     Absolute
Directory /home/ops/burt/backupFiles
Req File: /home/ops/burt/requestFiles/SR-DI.req
--- End BURT header
SR-CS-TEST-01:TESTPV 3 3.259328000000000e+00 4 -1
"""

IOC_RESTORE_BCD = """
--- Start BURT header
Time:     Tue May 13 17:25:52 2014
Login ID: ops-yhz16343 (Chris Bloomer)
Eff  UID: 37315
Group ID: 37315
Keywords: 
Comments: BSR-CS-TEST-01at 'zero'.
Type:     Absolute
Directory /home/ops/burt/backupFiles
Req File: /home/ops/burt/requestFiles/bcdorbit.req
--- End BURT header
SR-CS-TEST-01:BCD_LIMIT 1 20
SR-CS-TEST-01:SLEW_RATE 1 5
SR-CS-TEST-01:BCD_X_S1 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S2 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S3 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S4 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S5 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S6 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S7 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S8 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S9 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S10 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S11 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S12 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S13 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S14 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S15 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S16 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S17 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S18 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S19 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S20 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S21 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S22 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S23 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S24 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S25 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S26 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S27 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S28 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S29 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S30 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S31 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S32 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S33 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S34 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S35 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S36 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S37 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S38 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S39 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S40 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_X_S41 1 0.000000000000000e+00
SR-CS-TEST-01:BCD_Y_S42 1 0.000000000000000e+00
"""

IOC_RESTORE_ENUM = """
--- Start BURT header
Time:     Tue Sep 21 15:07:59 2010
Login ID: ops-cc83 (Chris Christou)
Eff  UID: 37245
Group ID: 37245
Keywords: hello world
Comments: Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4
Type:     Absolute
Directory /home/ops/burt/backupFiles
Req File: /home/ops/burt/requestFiles/SR-DI.req
--- End BURT header
SR-CS-TEST-01:TESTPV 1 DIAD
"""

IOC_RESTORE_LONG = """
--- Start BURT header
Time:     Tue Sep 21 15:07:59 2010
Login ID: ops-cc83 (Chris Christou)
Eff  UID: 37245
Group ID: 37245
Keywords: hello world
Comments: Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4
Type:     Absolute
Directory /home/ops/burt/backupFiles
Req File: /home/ops/burt/requestFiles/SR-DI.req
--- End BURT header
SR-CS-TEST-01:TESTPV_LONG 1 1.4000000000000000e+01
"""

IOC_RESTORE_SCALAR = """
--- Start BURT header
Time:     Tue Sep 21 15:07:59 2010
Login ID: ops-cc83 (Chris Christou)
Eff  UID: 37245
Group ID: 37245
Keywords: hello world
Comments: Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4
Type:     Absolute
Directory /home/ops/burt/backupFiles
Req File: /home/ops/burt/requestFiles/SR-DI.req
--- End BURT header
SR-CS-TEST-01:TESTPV 1 2
"""

MALFORMED_BOD = """
--- Start BURT header
Time:     Tue Sep 21 15:07:59 2010
Login ID: ops-cc83 (Chris Christou)
Eff  UID: 37245
Group ID: 37245
Keywords: hello world
Comments: Nominal optics\nInjection efficiency with IDs closed to 5mm is 80%\nResidual kick less than 1mm peak to peak\nOnly changed injection magnets\nRF phasing 94/180 voltage 0.8/1.4
Type:     Absolute
Directory /home/ops/burt/backupFiles
Req File: /home/ops/burt/requestFiles/SR-DI.req
--- End BURT header
SR01C-DI-COL-01:POS2 % Malformed PVs below
SR01C-DI-COL-02:POS1 -1.200000000000000e+01
SR01C-DI-COL-01:POS4
WO SR01C-DI-COL-01:POS5 1 1
random SR01C-DI-COL-01:POS6 1 1
nonexistent_pvSRO1C-DI-COL-02:POS99 2 1 1

SR01C-DI-COL-02:POS2 1 1.200000000000000e+01 % The PVs below are not malformed.
SR01C-DI-COL-03:POS3 3 666 111 222
"""

# @formatter:on
