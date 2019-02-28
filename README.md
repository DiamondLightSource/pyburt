# pyburt

pyburt is the Python version of the Burt EPICS extension. It utilizes the
[cothread](https://cothread.readthedocs.io/en/latest/) python library for Channel Access.

## Usage

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
$ pytest -vv
```
