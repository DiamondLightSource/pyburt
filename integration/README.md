# DLS integration tests for pyburt

Listed below are a set of instructions for running the DLS integration tests 
for the **snapshot** and
**restore** functionality of **pyburt**.

It involves running an IOC server which hosts a local IOC `SR-CS-TEST-01` and 
performing snapshots on DLS PV's, as well as restore operations on some `.snap` files 
which write to the below PV's:

```
SR-CS-TEST-01:TESTPV_FLOAT
SR-CS-TEST-01:TESTPV_ARR_FLOAT
SR-CS-TEST-01:TESTPV_LONG
SR-CS-TEST-01:TESTPV_ARR_LONG
SR-CS-TEST-01:TESTPV_DBL
SR-CS-TEST-01:TESTPV_ARR_DBL
SR-CS-TEST-01:TESTPV_STR
SR-CS-TEST-01:TESTPV_ENUM_STR
SR-CS-TEST-01:TESTPV_ARR_STR
SR-CS-TEST-01:TESTPV_CHAR
SR-CS-TEST-01:TESTPV_ARR_CHAR
SR-CS-TEST-01:TESTPV_SHORT
SR-CS-TEST-01:TESTPV_ARR_SHORT
```

It also involves doing some comparison tests against the vanilla BURT outputs, which 
requires running BURT on a set of `.req` and `.snap` files.

## Test Steps

1.) Open a terminal and run the test IOC server:

```bash
$ pwd
.../pyburt

$ integration/local_ioc.py
Starting iocInit
############################################################################
## EPICS R3.14.12.3 $Date: Mon 2012-12-17 14:11:47 -0600$
## EPICS Base built Nov  8 2018
############################################################################
iocRun: All initialization complete
Python 2.7.3 (default, Jan 18 2013, 21:33:46) 
[GCC 4.4.6 20120305 (Red Hat 4.4.6-4)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> 
```
2.) In a separate terminal, run the pytest integration tests via `pytest -vv
 integration`. This will perform some BURT restore calls on the test IOC 
 server, some snapshot tests on real PVs at DLS, as well
 as comparison tests against vanilla BURT.

Observe the output and check that all tests pass. This may take several seconds to complete:

```bash
$ pwd
.../pyburt

$ pytest -vv integration
=============================================================================================== test session starts ===============================================================================================
platform linux2 -- Python 2.7.13, pytest-4.3.1, py-1.8.0, pluggy-0.9.0 -- /scratch/tph19377/EPICS_REPOS/pyburt/venv/bin/dls-python
cachedir: .pytest_cache
rootdir: /scratch/tph19377/EPICS_REPOS/pyburt, inifile:
plugins: cov-2.6.1
collected 6 items                                                                                                                                                                                                 

integration/burt/test_restore.py::test_restore PASSED                                                                                                                                                       [ 16%]
integration/burt/test_restore.py::test_restore_group PASSED                                                                                                                                                 [ 33%]
integration/burt/test_snapshot.py::test_snapshot_normal PASSED                                                                                                                                              [ 50%]
integration/burt/test_snapshot.py::test_snapshot_group_normal PASSED                                                                                                                                        [ 66%]
integration/burt/test_snapshot.py::test_snapshot_invalid_save_len PASSED                                                                                                                                    [ 83%]
integration/burt/test_snapshot.py::test_burt_vanilla_rb PASSED                                                                                                                                              [100%]

============================================================================================ 6 passed in 19.62 seconds ============================================================================================
```