#!/usr/bin/env python3
import os
import sys
from pybpodapi.protocol import Bpod
from mouse2afc.mouse2afc import Mouse2AFC
bpod = Bpod()
Mouse2AFC(bpod).run()
