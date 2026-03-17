import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from tempfile import NamedTemporaryFile
from typing import IO, Any

import cothread
from cothread import catools
from epicsdbbuilder import (
    InitialiseDbd,
    ResetRecords,
    SetSimpleRecordNames,
    WriteRecords,
    records,
)

EPICS_SERVER_PORT = os.getenv("EPICS_CA_SERVER_PORT", "7064")
EPICS_REPEATER_PORT = os.getenv("EPICS_CA_REPEATER_PORT", "7065")

InitialiseDbd()
SetSimpleRecordNames()


@dataclass
class Record:
    """Represents a single record for use in an IOC.

    There is no ability to link records to each other.
    """

    typ: str
    name: str
    fields: dict[str, Any] = field(default_factory=dict)


class IocManager:
    def __init__(self) -> None:
        """Create new instance of IocManager.

        IOC will start using defined EPICS environment variables.
        """
        self.record_list: list[Record] = []
        self.db_file: IO = NamedTemporaryFile("w+t")
        self.process: subprocess.Popen | None = None

    def _add_record(self, typ, pv_name, **fields):
        assert not self.is_started(), (
            f"Cannot add {typ} record to running IOC ({pv_name})"
        )
        self.record_list.append(Record(typ, pv_name, fields))

    def _generate_db_file(self) -> None:
        """Convert the list of records into the equivalent db file.

        Note that epicsdbbuilder is currently unable to handle multiple independent
        record sets. As a result, we keep all of that code in this function, and reset
        before and after use.
        """
        ResetRecords()

        for record in self.record_list:
            getattr(records, record.typ)(record.name, **record.fields)

        WriteRecords(self.db_file.name)
        ResetRecords()

    def start_ioc(self) -> None:
        """Launch IOC."""
        self._generate_db_file()
        with open(self.db_file.name) as f:
            logging.debug(f.read())

        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "epicscorelibs.ioc",
                "-d",
                self.db_file.name,
            ],  # noqa (?)
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env={
                "EPICS_CA_SERVER_PORT": EPICS_SERVER_PORT,
                "EPICS_CA_REPEATER_PORT": EPICS_REPEATER_PORT,
            },
        )
        self.wait_for_ioc()

    def exit_ioc(self) -> None:
        """Close the soft IOC."""
        if self.process is not None:
            self.process.communicate("exit")
            self.process = None

        # Ensure that any cached connections are cleared in case
        # they appear in a new IOC later.
        # This is not cothread API.
        catools._channel_cache.purge()

    def is_started(self):
        return self.process is not None

    def wait_for_ioc(self, timeout: float = 5) -> None:
        start = time.time()
        while True:
            assert self.process is not None
            assert self.process.stdout is not None
            assert time.time() - start < timeout
            line = self.process.stdout.readline()
            if line:
                logging.info(f">>> {line.strip()}")
            cothread.Yield()
            if "complete" in line:
                # out, err = self.process.communicate("ioc('dbl')")
                # if out:
                #    logging.info(out)
                return

    def add_waveform_record(self, pv_name, length, ftvl="DOUBLE", **fields):
        """Add a new waveform PV record."""
        final_fields = {"NELM": length, "FTVL": ftvl}
        final_fields.update(fields)

        self._add_record("waveform", pv_name, **final_fields)

    def add_ai_record(self, pv_name, initial_value=0.0, **fields):
        """Add a new float-valued ai PV record."""
        final_fields = {"VAL": initial_value}
        final_fields.update(fields)

        self._add_record("ai", pv_name, **final_fields)

    def add_ao_record(self, pv_name, initial_value=0.0, **fields):
        """Add a new float-valued ao PV record."""
        final_fields = {"VAL": initial_value}
        final_fields.update(fields)

        self._add_record("ao", pv_name, **final_fields)

    def add_bi_record(self, pv_name, **fields):
        """Add a new binary-valued bi PV record."""
        self._add_record("bi", pv_name, **fields)

    def add_bo_record(self, pv_name, **fields):
        """Add a new binary-valued bo PV record."""
        self._add_record("bo", pv_name, **fields)

    def add_stringin_record(self, pv_name, **fields):
        """Add a new stringin PV record."""
        self._add_record("stringin", pv_name, **fields)

    def add_stringout_record(self, pv_name, **fields):
        """Add a new stringout PV record."""
        self._add_record("stringout", pv_name, **fields)

    def add_longin_record(self, pv_name, **fields):
        """Add a new longin PV record."""
        self._add_record("longin", pv_name, **fields)

    def add_longout_record(self, pv_name, **fields):
        """Add a new longout PV record."""
        self._add_record("longout", pv_name, **fields)

    def add_mbbi_record(self, pv_name, states, **fields):
        """Add a new mbbi PV record."""
        nstates = len(states)
        assert nstates <= 16, (
            f"mbbi record does not support more than 16 states ({nstates} requested)"
        )
        states.extend([""] * (16 - nstates))

        final_fields = self.build_mbbx_fields(states)
        final_fields.update(fields)

        self._add_record("mbbi", pv_name, **final_fields)

    def add_mbbo_record(self, pv_name, states, **fields):
        """Add a new mbbo PV record."""
        nstates = len(states)
        assert nstates <= 16, (
            f"mbbo record does not support more than 16 states ({nstates} requested)"
        )
        states.extend([""] * (16 - nstates))

        final_fields = self.build_mbbx_fields(states)
        final_fields.update(fields)

        self._add_record("mbbo", pv_name, **final_fields)

    @staticmethod
    def build_mbbx_fields(states):
        """Build the kwarg dictionary for an MBBI or MBBO record with the given states.

        Args:
            states: list of (string) values for MBBx record

        Returns:
            dict of PV record fields for record construction
        """
        number_names = [
            "ZR",
            "ON",
            "TW",
            "TH",
            "FR",
            "FV",
            "SX",
            "SV",
            "EI",
            "NI",
            "TE",
            "EL",
            "TV",
            "TT",
            "FT",
            "FF",
        ]

        # Create the correct number of keyword arguments to mbbi/mbbo:
        # ZRST=states[0], ZRVL=0, etc.
        st_dict = {nn + "ST": s for nn, s in zip(number_names, states, strict=False)}
        vl_dict = {nn + "VL": i for i, nn in enumerate(number_names)}

        # All calls use VAL=0, PINI='YES'
        fields = {"VAL": 0, "PINI": "YES"}
        fields.update(st_dict)
        fields.update(vl_dict)

        return fields
