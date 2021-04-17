import logging
import time
from unittest.mock import MagicMock, patch

import cothread
from cothread.catools import caget, caput
from cothread.pv import PV

from tests.ioc_manager import IocManager
from unittest import TestCase

MYPV = "BLXXI-CS-FILL-01:MYPV01"


class PVTest(TestCase):
    ioc_manager = IocManager()

    @classmethod
    def setUpClass(cls):
        # Build a very soft IOC
        cls.ioc_manager.addAIRecord(MYPV)
        cls.ioc_manager.startIoc()

    def setUp(self):
        # initialise
        caput(MYPV, 1)

    def tearDown(self):
        caput(MYPV, 1)

    @classmethod
    def tearDownClass(cls):
        cls.ioc_manager.exitIoc()

    def test_ioc_setup(self):
        """Test that the IOC is working as expected."""
        caget(MYPV)
        test_value = 6.5
        caput(MYPV, test_value)
        x = caget(MYPV)
        self.assertEqual(test_value, x)
