"""Determine a pyburt output from a cothread PV type.

The output/input type from a caget value to a .snap, .rgr file, or when caputting a
new value is dependent on the type ofthe caget value; there are special conversion rules
implemented in the old BURT which are mimicked here.

This module provides an interface for obtaining and setting channel access pv types
from cothread. A visitor pattern is implemented to avoid lengthy if/else case statements
and to take advantage of the new Python 3 single-dispatch generic functions.

The type mapping from a python type to a CA DBR type is as follows:

python int -> DBR_LONG
python float -> DBR_DOUBLE
python string -> DBR_STRING
"""
import logging
from abc import ABCMeta, abstractmethod
from functools import singledispatch
from typing import Any

import cothread

# EPICS constraint, max 39 characters in a channel access string.
MAX_DBR_STR_LEN = 39

# Scalar pv entries are shown as a 15 width precision number(s) in scientific notation.
SNAP_PRECISION_PYFORMAT = "{:.15e}"


class PvVisitor:
    """Abstract base class for PV visitors."""

    __metaclass__ = ABCMeta

    @singledispatch
    def visit(self, dbr_val: object) -> None:
        """Handle generic case."""
        logging.warning(f"Unexpected cothread DBR type: {type(dbr_val)}, {dbr_val}.")
        return None

    @abstractmethod
    @visit.register(cothread.dbr.ca_str)
    def visit(self, dbr_val: cothread.dbr.ca_str) -> Any:
        """Handle string (DBR_STRING) type."""
        pass

    @abstractmethod
    @visit.register(cothread.dbr.ca_int)
    def visit(self, dbr_val: cothread.dbr.ca_int) -> Any:
        """Handle int (DBR_LONG) type."""
        pass

    @abstractmethod
    @visit.register(cothread.dbr.ca_float)
    def visit(self, dbr_val: cothread.dbr.ca_float) -> Any:
        """Handle float (DBR_DOUBLE) type."""
        pass

    @abstractmethod
    @visit.register(cothread.dbr.ca_array)
    def visit(self, dbr_val: cothread.dbr.ca_array) -> Any:
        """Handle CA array type."""
        pass


class PvReadVisitor(PvVisitor):
    """Convert and prepare a DBR value for writing to a BURT file."""

    @singledispatch
    def visit(self, dbr_val: object) -> str:
        """Handle generic case."""
        return SNAP_PRECISION_PYFORMAT.format(dbr_val)

    @visit.register(cothread.dbr.ca_str)
    def visit(self, dbr_val: cothread.dbr.ca_str) -> str:
        """Handle string (DBR_STRING) type."""
        return str(dbr_val)

    @visit.register(cothread.dbr.ca_int)
    def visit(self, dbr_val: cothread.dbr.ca_int) -> str:
        """Handle int (DBR_LONG) type."""
        return SNAP_PRECISION_PYFORMAT.format(dbr_val)

    @visit.register(cothread.dbr.ca_float)
    def visit(self, dbr_val: cothread.dbr.ca_float) -> str:
        """Handle float (DBR_DOUBLE) type."""
        return SNAP_PRECISION_PYFORMAT.format(dbr_val)

    @visit.register(cothread.dbr.ca_array)
    def visit(self, dbr_val: cothread.dbr.ca_array) -> list:
        """Handle CA array type."""
        return [SNAP_PRECISION_PYFORMAT.format(reading) for reading in dbr_val[:]]


class PvWriteVisitor(PvVisitor):
    """Convert and prepare a DBR value for writing via channel access."""

    @singledispatch
    def visit(self, dbr_val: object) -> str:
        """Handle generic case."""
        return str(dbr_val)

    @visit.register(cothread.dbr.ca_str)
    def visit(self, dbr_val: cothread.dbr.ca_str) -> str:
        """Handle string (DBR_STRING) type."""
        return str(dbr_val)

    @visit.register(cothread.dbr.ca_int)
    def visit(self, dbr_val: cothread.dbr.ca_int) -> int:
        """Handle int (DBR_LONG) type."""
        return int(dbr_val)

    @visit.register(cothread.dbr.ca_float)
    def visit(self, dbr_val: cothread.dbr.ca_float) -> float:
        """Handle float (DBR_DOUBLE) type."""
        return float(dbr_val)

    @visit.register(cothread.dbr.ca_array)
    def visit(self, dbr_val: cothread.dbr.ca_array) -> list:
        """Handle CA array type."""
        return [self.visit(val) for val in dbr_val]


class PvTypeDBR:
    """Encapsulate PV types and convert to DBR format."""

    def __init__(self, dbr_val) -> None:
        """Init constructor."""
        self.dbr_val = dbr_val

    def accept(self, type_visitor: PvVisitor) -> Any:
        """Single dispatch on the DBR type to get the desired value."""
        return type_visitor.visit(self.dbr_val)
