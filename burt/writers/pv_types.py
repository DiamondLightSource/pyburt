"""Determine a pyburt output from a cothread PV type.

The output/input type from a caget value to a .snap, .rgr file, or when caputting a
new value is dependent on the type ofthe caget value; there are special conversion rules
implemented in the old BURT which are mimicked here.

This module provides an interface for obtaining and setting channel access pv types
from cothread. A visitor pattern is implemented to avoid lengthy if/else case statements
and to take advantage of the new Python 3 single-dispatch generic functions.
"""
import logging
from abc import ABCMeta, abstractmethod
from functools import singledispatch
from typing import Any, Dict, List, Tuple

import cothread


class PvVisitor:
    """Abstract base class for PV visitors."""
    __metaclass__ = ABCMeta

    @singledispatch
    def visit(self, dbr_val: object) -> None:
        """Generic case."""
        logging.warning(f"Unexpected cothread DBR type: {type(dbr_val)}, {dbr_val}.")
        return None

    @abstractmethod
    @visit.register(cothread.dbr.ca_str)
    def visit(self, dbr_val: cothread.dbr.ca_str) -> str:
        """Visit string type."""
        pass


class PvReadVisitor(PvVisitor):
    """Convert and prepare a DBR value for writing to a BURT file."""

    @singledispatch
    def visit(self, dbr_val: object) -> None:
        """Generic case."""
        return super(PvReadVisitor, self).visit(dbr_val)

    @visit.register(cothread.dbr.ca_str)
    def visit(self, dbr_val: cothread.dbr.ca_str) -> str:
        """Visit string type."""
        return str(dbr_val)

    @visit.register(cothread.dbr.ca_str)
    def visit(self, dbr_val: cothread.dbr.ca_str) -> int:
        """Generic visit."""
        return str(dbr_val)


class PvWriteVisitor(PvVisitor):
    """Convert and prepare a DBR value for writing via channel access."""

    @singledispatch
    def visit(self, dbr_val: object) -> None:
        """Generic case."""
        return super(PvWriteVisitor, self).visit(dbr_val)

    @visit.register(cothread.dbr.ca_str)
    def visit(self, dbr_val: cothread.dbr.ca_str) -> str:
        """Visit string type."""
        return str(dbr_val)

    @visit.register(cothread.dbr.ca_str)
    def visit(self, dbr_val: cothread.dbr.ca_str) -> int:
        """Generic visit."""
        return str(dbr_val)


class PvTypeDBR:
    def __init__(self, dbr_val) -> None:
        self.dbr_val = dbr_val

    def accept(self, type_visitor: PvVisitor) -> Any:
        return type_visitor.visit(self.dbr_val)
