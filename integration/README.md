# Integration tests for pyburt

Listed below are a set of instructions for running the integration tests for the **snapshot** and
**restore** functionality of **pyburt**.

It involves running an IOC server which hosts a dummy PV `SR-CS-TEST-01:TESTPV` and performing restore
operations on some `.snap` files which write to this PV. It also involves
doing some comparison tests against the vanilla BURT outputs, which requires running BURT on a set of
`.req` and `.snap` files.

## Test Steps

1.) Open a terminal and run the test IOC server:

```bash
$ pwd
.../pyburt

$ test/integration/test_ioc.py
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
2.) In a separate terminal, run the pytest integration tests. This will perform some BURT restore
calls on the test IOC server, as well as comparison tests against vanilla BURT.

Observe the output and check that all tests pass. This may take several seconds to complete:

```bash
$ pwd
.../pyburt

$ pytest -v integration
============================= test session starts ==============================
platform linux2 -- Python 2.7.13, pytest-3.2.1, py-1.4.34, pluggy-0.4.0 -- /dls_sw/prod/tools/RHEL7-x86_64/Python/2-7-13/prefix/bin/python
cachedir: .cache
rootdir: /scratch/tph19377/EPICS_REPOS/pyburt, inifile:
collected 1 item                                                                

integration/test_integration.py::test_restore_integration PASSED

=========================== 1 passed in 0.24 seconds ===========================
```