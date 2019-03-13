""" Various parsers which read BURT related input/output files and
encapsulates the information."""
import burt
import cothread
from pkg_resources import require

require('cothread')

from cothread.catools import caget, caput


class PV:
    """ Stores the information of a PV in a parsed .snap or .req file, and
    provides functionality to save or restore a PV's current state.

    Attributes:
        name (str): The name of the PV.
        vals (list): A list of strings containing the PV values. This will be a
            singleton list if the data type of the PV is not a CA array.
        is_readonly (bool): Whether the PV is read only, or not. If so, it is
        not restored by pyburt.restore()
        is_readonly_notify (bool): Whether the PV is a read-only-notify type.
        dtype_len (int): The length of the PV reading. If it is a CA array,
            this will be set to the length of the array, otherwise it is set
            to 1.
    """

    def __init__(self, name, vals=None, is_readonly=False,
                 is_readonly_notify=False):
        """ Constructor.

        Args:
            name (str): The name of the PV.
            vals (list): A list of floats containing the PV values.
            is_readonly (bool): Whether the PV is read only, or not.
        """
        self.name = name
        self.vals = vals
        self.is_readonly = is_readonly
        self.is_readonly_notify = is_readonly_notify
        self.dtype_len = 1 if vals is None else len(vals)

    def __eq__(self, other):
        """ Equality operator override

        Args:
            other (PV): PV object to compare

        Returns:
            bool: If other is equal to self or not
        """
        eq = False

        if isinstance(other, type(self)):
            eq = (self.name == other.name) and \
                 (self.vals == other.vals) and \
                 (self.is_readonly == other.is_readonly) and \
                 (self.is_readonly_notify == other.is_readonly_notify) and \
                 (self.dtype_len == other.dtype_len)
            return eq
        else:
            return NotImplemented

    def __ne__(self, other):
        """ Non equality operator override (unnecessary in Python 3).

        Args:
            other (PV): PV object to compare

        Returns:
            bool: If other is not equal to self or not

        """
        if (self == other) is not NotImplemented:
            return not (self == other)
        else:
            return NotImplemented

    def __hash__(self):
        """ Hash table entry override.

        Returns:
            int: The hash table entry.
        """
        return hash((self.name, self.vals, self.is_readonly,
                     self.is_readonly_notify, self.dtype_len))

    def __repr__(self):
        """ Class representation override.

        Returns:
            str: The class representation.
        """
        return str(self.__class__) + ": " + str(self.__dict__)

    def __str__(self):
        """ To string override.

        Returns:
            str: The string representation of the class.
        """
        return self.__repr__()

    def snapshot(self):
        """ Takes a snapshot of the PV's current state by storing the values as
            a formatted string to be placed in a .snap file.

        The .snap file PV entries require a 15 width precision number(s) in
        scientific notation.

        Returns:
            str: The .snap file entry for the PV.
        """
        ca_reading = caget(self.name, datatype=cothread.catools.DBR_ENUM_STR)

        # caget returns either a scalar or a ca array, and the pv entry in the
        # .snap file requires the type length.
        ca_reading_len = 1
        ca_reading_str = ""

        if isinstance(ca_reading, cothread.dbr.ca_array):
            ca_reading_len = len(ca_reading)
            # Flattening ca_array
            ca_reading_str = " ".join(
                ["{:.15e}".format(reading) for reading in ca_reading])

        # A DBR enum, e.g. "DIAD".
        elif isinstance(ca_reading, cothread.dbr.ca_str):
            ca_reading_str = str(ca_reading)

        else:
            ca_reading_str = "{:.15e}".format(ca_reading)

        snapshot_entry = ""
        if self.is_readonly:
            snapshot_entry += burt.READONLY_SPECIFIER + " "
        elif self.is_readonly_notify:
            snapshot_entry += burt.READONLY_NOTIFY_SPECIFIER + " "

        snapshot_entry += "{} {} {}".format(self.name, ca_reading_len,
                                            ca_reading_str)

        return snapshot_entry

    def restore(self):
        """ Restores a PV to its saved state. If the PV is specified as read
            only, do nothing.
        """
        if not self.is_readonly or not self.is_readonly_notify:
            caput(self.name, self.vals)

        # TODO: write to the no write snapshot file
        if self.is_readonly_notify:
            pass
