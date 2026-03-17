[![CI](https://github.com/DiamondLightSource/pyburt/actions/workflows/ci.yml/badge.svg)](https://github.com/DiamondLightSource/pyburt/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/DiamondLightSource/pyburt/branch/main/graph/badge.svg)](https://codecov.io/gh/DiamondLightSource/pyburt)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# burt

Python version of the BackUp and ResTore tool

This is where you should write a short paragraph that describes what your module does,
how it does it, and why people should use it.

Source          | <https://github.com/DiamondLightSource/pyburt>
:---:           | :---:
Docker          | `docker run ghcr.io/diamondlightsource/pyburt:latest`
Releases        | <https://github.com/DiamondLightSource/pyburt/releases>


## API Usage

```python
import burt

# Saves PV values in a single .req file into a .snap file along with some additional
# metadata.
burt.take_snapshot(["/path/to/.req/file.req"],
    "/path/to/.snap/file.snap", "comment", "keywords")

# As above, except take a snapshot of several .req files, combining the values into
# one .snap file.
burt.take_snapshot(["/path/to/.req/file.req", "/path/to/.req/file2.req"],
    "/path/to/.snap/file.snap", "comment", "keywords")
    
# Restores PV values in a .snap file.
burt.restore("/path/to/.snap/file.snap")

# Specify a restore group to restore.
burt.restore_group("/path/to/.rgr/file.rgr")
    
# TODO: specify a request group to take a snapshot of.
burt.take_snapshot_group("/path/to/.rqg/file.rqg",
    "/path/to/.snap/file.snap", "comment", "keywords")
```

## CLI Usage

```bash
$ burt-read -h
usage: burt-read [-h] [-c C] [-k K] [-v] [-l L] request_file snap_destination

positional arguments:
  request_file      The path to either a .req or .rqg file.
  snap_destination  The path to the destination .snap file.

optional arguments:
  -h, --help        show this help message and exit
  -c C              Optional snapshot comments.
  -k K              Optional snapshot keywords.
  -v                Enable verbose logging (debug) level.
  -l L              Optional backup log file destination.
```

```bash
$ burt-write -h
usage: burt-write [-h] [-v] [-l L] restore_file

positional arguments:
  restore_file  The path to either a .snap or .rgr file.

optional arguments:
  -h, --help    show this help message and exit
  -v            Enable verbose logging (debug) level.
  -l L          Optional restore log file destination.
```

## Tests
Before running any tests, make sure you build and run the devcontainer.

#### Unit Tests
To run the core pytest unit tests:

```bash
$ pytest tests/unit/
```

Note: the unit tests should be run from the root project directory.

#### DLS Integration Tests

There are separate DLS integration tests for pyburt. These tests run snapshot
and restore operations against a soft IOC (see `tests/integration/softioc.py`).

To run both integration and unit tests:

```bash
$ pytest
```
