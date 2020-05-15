# DLS integration tests for pyburt

Listed below are a set of instructions for running the DLS integration tests
for the **snapshot** and
**restore** functionality of **pyburt**.

## Soft IOC

`softioc.db` contains all the types of PVs that Pyburt can handle. There is also
`softioc.req` and `softioc.burt.snap`, which shows how the original Burt
saves these values. To run this IOC

```
softIoc -d softioc.db
```

## Integration tests.

These involves running an IOC server which hosts a local IOC `SR-CS-TEST-01` and
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

$ softIoc -d test/integration/softioc.db
dbLoadDatabase("/home/will/code/epics-base/bin/linux-x86_64/../../dbd/softIoc.dbd")
softIoc_registerRecordDeviceDriver(pdbbase)
dbLoadRecords("test/integration/softioc.db")
iocInit()
Starting iocInit
############################################################################
## EPICS R7.0.3.2-DEV
## Rev. R7.0.3.1-220-g514962724234c0777a42
############################################################################
iocRun: All initialization complete
epics>
```

2.) In a separate terminal, run the pytest integration tests via `pipenv run python -m pytest test/integration`.
This will perform some BURT restore calls on the test IOC
server, some snapshot tests on real PVs at DLS, as well
as comparison tests against vanilla BURT.

Observe the output and check that all tests pass. This may take several seconds to complete:

```bash
$ pwd
.../pyburt

$ pipenv run python -m pytest -vv test/integration
========================================== test session starts ==========================================
platform linux -- Python 3.6.9, pytest-5.0.0, py-1.8.0, pluggy-0.12.0 -- /home/will/.local/share/virtualenvs/pyburt-6wgA0aKN/bin/python
cachedir: .pytest_cache
rootdir: /home/will/code/pyburt
plugins: cov-2.7.1
collected 14 items

test/integration/burt/test_restore.py::test_restore PASSED                                        [  7%]
test/integration/burt/test_restore.py::test_restore_long PASSED                                   [ 14%]
test/integration/burt/test_restore.py::test_restore_string PASSED                                 [ 21%]
test/integration/burt/test_restore.py::test_restore_enum err PASSED                               [ 28%]
test/integration/burt/test_restore.py::test_restore_group PASSED                                  [ 35%]
test/integration/burt/test_restore.py::test_speed_restore SKIPPED                                 [ 42%]
test/integration/burt/test_restore.py::test_various_types_restore PASSED                          [ 50%]
test/integration/burt/test_snapshot.py::test_snapshot_normal SKIPPED                              [ 57%]
test/integration/burt/test_snapshot.py::test_snapshot_group_normal XFAIL                          [ 64%]
test/integration/burt/test_snapshot.py::test_snapshot_req_file_length_bigger_than_pv PASSED       [ 71%]
test/integration/burt/test_snapshot.py::test_burt_vanilla_rb XFAIL                                [ 78%]
test/integration/burt/test_snapshot.py::test_speed_snapshot SKIPPED                               [ 85%]
test/integration/burt/test_snapshot.py::test_various_types_against_burt SKIPPED                   [ 92%]
test/integration/burt/test_snapshot.py::test_speed_snapshot_group SKIPPED                         [100%]

============================ 7 passed, 5 skipped, 2 xfailed in 0.59 seconds =============================
```
