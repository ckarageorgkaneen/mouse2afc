import logging

from data import Data
from state_matrix import StateMatrix
from task_parameters import TaskParameters


logger = logging.getLogger(__name__)


class Mouse2AFCError(Exception):
    pass


def error(message):
    logger.error(message)
    raise Mouse2AFCError(message)

NumTrialsToGenerate = 1
StartFrom = 0

class Mouse2AFC:
    def __init__(self, bpod, config_file=None):
        self._bpod = bpod
        self._task_parameters = TaskParameters(
            file_=config_file).task_parameters
        self._data = Data(self._bpod.session, self._task_parameters)

    def _set_current_stimulus(self):
        # Set current stimulus for next trial - set between -100 to +100
        self._task_parameters.CurrentStim = (self._data.Custom.Trials.DV[0] + (
            int(self._data.Custom.Trials.DV[0] > 0) or -1)) / 0.02

    def run(self):
        self._data.Custom.assign_future_trials(StartFrom,NumTrialsToGenerate)
        self._set_current_stimulus()
        i_trial = 0
        while True:
            logger.error('Before StateMatrix()')
            sma = StateMatrix(
                self._bpod, self._task_parameters, self._data, i_trial)
            logger.error('Before send_state_machine()')
            self._bpod.send_state_machine(sma)
            logger.error('Before run_state_machine()')
            if not self._bpod.run_state_machine(sma):
                break
            self._data.Custom.update(i_trial)
            i_trial += 1
