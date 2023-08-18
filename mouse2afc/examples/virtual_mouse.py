#!/usr/bin/env python3
"Creates a 'virutal mouse' for testing a protocol without a BPod"
import itertools
import logging
import random
import time

from concurrent.futures import ThreadPoolExecutor

from pybpodapi.protocol import Bpod

logger = logging.getLogger(__name__)


class MouseError(Exception):
    pass


def _error(message):
    logger.error(message)
    raise MouseError(message)


class Mouse:
    """A `ThreadPoolExecutor` wrapper for spawning a 'virtual mouse' that can
       manually override the Mouse2AFC protocol"""
    _START_TRIAL_DELAY = 2
    _CHOICE_DELAY = 2
    _DEFAULT_PORT_VALUE = 5
    _CENTER_PORT_NUM = 2
    _NON_CENTER_PORT_NUMS = [1, 3]

    def __init__(self, bpod):
        self._bpod = bpod
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._future = None

    def _put_nose_in_port(self, port_num):
        self._bpod.manual_override(Bpod.ChannelTypes.INPUT, 'Port',
                                   channel_number=port_num,
                                   value=self._DEFAULT_PORT_VALUE)

    def _be(self):
        """Act like a mouse in a Mouse2AFC experiment."""
        for _ in itertools.count():
            time.sleep(self._START_TRIAL_DELAY)
            time.sleep(self._CHOICE_DELAY)
            self._put_nose_in_port(self._CENTER_PORT_NUM)
            time.sleep(self._CHOICE_DELAY)
            self._put_nose_in_port(random.choice(self._NON_CENTER_PORT_NUMS))

    def spawn(self):
        if self._future is not None:
            _error('Already spawned.')
        self._future = self._executor.submit(self._be)
