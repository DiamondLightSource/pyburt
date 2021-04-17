import logging
import os
import subprocess
import sys
import time
from tempfile import NamedTemporaryFile
from typing import Optional

import cothread
from cothread import catools

from tests.db_templates import (
    AI_TEMPLATE,
    BI_TEMPLATE,
    MBBI_TEMPLATE,
    MBBO_TEMPLATE,
    STRINGIN_TEMPLATE,
    WAVEFORM_TEMPLATE,
)

EPICS_SERVER_PORT = os.getenv("EPICS_CA_SERVER_PORT", "7064")
EPICS_REPEATER_PORT = os.getenv("EPICS_CA_REPEATER_PORT", "7065")


class IocManager:
    def __init__(self) -> None:
        """Create new instance of IocManager.

        IOC will start using defined EPICS environment variables.
        """
        self.db_string = ""
        self.db_file = NamedTemporaryFile("w+t")
        self.process: Optional[subprocess.Popen] = None

    def startIoc(self) -> None:
        """Launch IOC."""
        logging.debug(self.db_string)
        self.db_file.write(self.db_string)
        self.db_file.flush()
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

    def exitIoc(self) -> None:
        """Close the soft IOC."""
        if self.process is not None:
            self.process.communicate("exit")
            self.process = None

        # Ensure that any cached connections are cleared in case
        # they appear in a new IOC later.
        # This is not cothread API.
        catools._channel_cache.purge()

    def isStarted(self):
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

    def addRecords(self, path):
        """Add records from the given db file."""
        assert not self.isStarted(), "Cannot add records to running IOC"
        with open(path) as f:
            self.db_string += f.read()

    def addWaveformRecord(self, pvName, length, ftvl="DOUBLE"):
        """Add a new float-valued PV waveform record."""
        assert (
            not self.isStarted()
        ), f"Cannot add Waveform record to running IOC ({pvName})"
        self.db_string += WAVEFORM_TEMPLATE.format(pvName, length, ftvl)

    def addAIRecord(self, pvName, initial_value=0.0):
        """Add a new float-valued PV AI record."""
        assert not self.isStarted(), "Cannot add AI record to running IOC (%s)" % pvName
        self.db_string += AI_TEMPLATE.format(pvName, initial_value)

    def addBIRecord(self, pvName):
        """Add a new binary-valued PV AI record."""
        assert not self.isStarted(), "Cannot add BI record to running IOC (%s)" % pvName
        self.db_string += BI_TEMPLATE.format(pvName)

    def addBORecord(self, pvName):
        """Add a new binary-valued PV AI record."""
        assert not self.isStarted(), "Cannot add BO record to running IOC (%s)" % pvName
        raise NotImplementedError()

    def addStringInRecord(self, pvName):
        """Add a new stringin PV record."""
        assert not self.isStarted(), (
            "Cannot add stringin record to running IOC (%s)" % pvName
        )
        self.db_string += STRINGIN_TEMPLATE.format(pvName)

    def addStringOutRecord(self, pvName):
        """Add a new stringout PV record."""
        assert not self.isStarted(), (
            "Cannot add stringout record to running IOC (%s)" % pvName
        )
        raise NotImplementedError()

    def addMBBIRecord(self, pvName, states):
        """Add a new MBBI PV record."""
        assert not self.isStarted(), f"Cannot add MBBI record to running IOC ({pvName})"
        nstates = len(states)
        assert (
            nstates <= 16
        ), f"MBBI record does not support more than 16 states ({nstates} requested)"
        states.extend([""] * (16 - nstates))
        self.db_string += MBBI_TEMPLATE.format(pvName, *states)

    def addMBBORecord(self, pvName, states):
        """Add a new MBBI PV record."""
        assert not self.isStarted(), (
            "Cannot add MBBO record to running IOC (%s)" % pvName
        )
        nstates = len(states)
        assert (
            nstates <= 16
        ), f"MBBO record does not support more than 16 states ({nstates} required)"
        states.extend([""] * (16 - nstates))
        self.db_string += MBBO_TEMPLATE.format(pvName, *states)

    @staticmethod
    def split_pvname(pvName):
        """Split the PV name into the ioc_name and PV name.

        If the PV name contains multiple ':', e.g. ioc:ILKS:STATE
        identify everything before the first ':' as the IOC name
        """
        (ioc_name, record_name) = pvName.split(":", 1)
        return ioc_name, record_name

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
        st_dict = {nn + "ST": s for nn, s in zip(number_names, states)}
        vl_dict = {nn + "VL": i for i, nn in enumerate(number_names)}

        # All calls use VAL=0, PINI='YES'
        kwargs = {"VAL": 0, "PINI": "YES"}
        kwargs.update(st_dict)
        kwargs.update(vl_dict)

        return kwargs
