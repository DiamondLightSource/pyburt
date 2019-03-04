# pyburt

**pyburt** is the Python version of the Burt EPICS extension. It utilizes the
[cothread](https://cothread.readthedocs.io/en/latest/) python library for Channel Access.

## Usage

```python
from burt import pyburt
# Saves PV values in a .req file into a .snap file along with some additional metadata.
pyburt.take_snapshot("/path/to/.req/file.req",
    "/path/to/.snap/file.snap", "comment", "keywords")

# Restores PV values in the .snap file.
pyburt.restore("/path/to/.snap/file.snap")
```

## Build

To build the Sphinx documentation:

```bash
$ cd docs
$ make html
```

The generated pages are in `docs/_build/html`.

## Test

To run the pytest tests:

```bash
$ pipenv shell
$ pytest -v test
```

There are separate integration tests for testing the `restore` functionality of pyburt. See
`integration/README.md` for instructions.

Note that running pytest against `integration` without running the test IOC first,
as described in `integration/README.md`, will cause the tests to
fail.