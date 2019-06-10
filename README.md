[![Build Status](https://travis-ci.com/dls-controls/pyburt.svg?branch=master)](https://travis-ci.com/dls-controls/pyburt)
[![Coverage Status](https://coveralls.io/repos/github/dls-controls/pyburt/badge.svg?branch=master)](https://coveralls.io/github/dls-controls/pyburt?branch=master)
[![Documentation Status](https://readthedocs.org/projects/pyburt/badge/?version=latest)](https://pyburt.readthedocs.io/en/latest/?badge=latest)

# pyburt

**pyburt** is the Python version of the Burt EPICS extension. It utilizes the
[cothread](https://cothread.readthedocs.io/en/latest/) python library for
Channel Access.

## Documentation

Full documentation is available at [Read the Docs](https://readthedocs.org/projects/pyburt/).

## Usage

```python
import burt

# Saves PV values in a .req file into a .snap file along with some additional
# metadata.
burt.take_snapshot("/path/to/.req/file.req",
    "/path/to/.snap/file.snap", "comment", "keywords")
    
# Specify a request group to take a snapshot of.
burt.take_snapshot_group("/path/to/.rqg/file.rqg",
    "/path/to/.snap/file.snap", "comment", "keywords")

# Restores PV values in a .snap file.
burt.restore("/path/to/.snap/file.snap")

# Specify a restore group to restore.
burt.restore_group("/path/to/.rgr/file.rgr")
```

## Installation

To install the latest version of pyburt using pip:

```bash
$ pip install pyburt
```

## Build
 
To build the Sphinx documentation:

```bash
$ cd docs
$ make html
```

The generated pages are in `docs/_build/html`.

## Licence

See [LICENSE](). 

## Tests

#### Unit Tests
To run the core pytest unit tests:

```bash
$ pwd
.../pyburt

$ pipenv shell
(pyburt) $ pytest -vv test
```

Note: the unit tests should be run from the root project directory.

#### DLS Integration Tests

There are separate DLS integration tests for pyburt. These tests run snapshot
and restore operations against known Diamond PV's. See 
`integration/README.md` for instructions.

Note that running pytest against `integration` without running the test IOC
 first,
as described in `integration/README.md`, will cause the tests to
fail.

#### Pytac Integration Tests

Similarly, there are integration tests designed for testing against known PV's
defined in Pytac.
