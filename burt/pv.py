""" Represents a PV in a BURT file."""
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
        save_len (int): Relevant only if the PV is a ca array type; only the
            first save_len elements of the PV's ca array is saved on a
            snapshot.
        is_readonly (bool): Whether the PV is read only, or not. If so, it is
            not restored by pyburt.restore()
        is_readonly_notify (bool): Whether the PV is a read-only-notify type.
        is_writeonly (bool): Whether the PV is a write-only type.
    """

    def __init__(self, name, vals=None, save_len=None, is_readonly=False,
                 is_readonly_notify=False, is_writeonly=False):
        """ Constructor.

        Args:
            name (str): The name of the PV.
            vals (list): A list of strings containing the PV values. This will
                be a singleton list if the data type of the PV is not a CA
                array.
            save_len (int): Specifies the first save_len elements to save for a
                ca array. Only relevant if the PV's datatype is a ca array.
            is_readonly (bool): Whether the PV is read only, or not.
            is_readonly_notify (bool): Whether the PV is read only notify type.
            is_writeonly (bool): Whether the PV is a write-only type.
        """
        self.name = name
        self.vals = vals
        self.save_len = save_len
        self.is_readonly = is_readonly
        self.is_readonly_notify = is_readonly_notify
        self.is_writeonly = is_writeonly

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
                 (self.is_writeonly == other.is_writeonly) and \
                 (self.save_len == other.save_len)
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
                     self.is_readonly_notify, self.is_writeonly,
                     self.save_len))

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

    def gen_snapshot_entry(self):
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

            # User specified to save only save_len elements from ca_reading.
            if self.save_len:
                if self.save_len > ca_reading_len:
                    raise ValueError("Save length value specified in .req "
                                     "file exceeds length of PV data.")
                else:
                    ca_reading_len = self.save_len

            # Flattening ca_array
            ca_reading_str = " ".join(
                ["{:.15e}".format(reading) for reading in
                 ca_reading[:ca_reading_len]])

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
        elif self.is_writeonly:
            snapshot_entry += burt.WRITEONLY_SPECIFIER + " "

        snapshot_entry += "{} {} {}".format(self.name, ca_reading_len,
                                            ca_reading_str)

        return snapshot_entry

    def restore_values(self):
        """ Restores a PV to its saved state. If the PV is specified as read
            only, do nothing.
        """
        if not self.is_readonly or not self.is_readonly_notify:

            if self.is_writeonly:
                # TODO: write the "correct" value, not the saved ones.
                pass
            else:
                caput(self.name, self.vals)

        # TODO: write to the no write snapshot file
        if self.is_readonly_notify:
            pass
