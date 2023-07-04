#!/usr/bin/env python3
import os
import sys
sys.path.append('/home/henry/Documents/mouse2afc')
from pybpodapi.protocol import Bpod
from mouse2afc import Mouse2AFC
bpod = Bpod(emulator_mode=True)
Mouse2AFC(bpod).run()