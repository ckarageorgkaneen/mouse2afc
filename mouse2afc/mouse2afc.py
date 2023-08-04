import logging

import time

from mouse2afc.data import Data
from mouse2afc.state_matrix import StateMatrix
from mouse2afc.task_parameters import TaskParameters


logger = logging.getLogger(__name__)


class Mouse2AFCError(Exception):
    pass


def error(message):
    logger.error(message)
    raise Mouse2AFCError(message)

NUM_TRIALS_TO_GENERATE = 1
START_FROM = 0

class Mouse2AFC:
    def __init__(self, bpod, config_file=None):
        self._bpod = bpod
        self._task_parameters = TaskParameters(
            file_=config_file).task_parameters
        self._data = Data(self._bpod.session, self._task_parameters)

    def my_softcode_handler(self,_softcode):
        "Defines what each SoftCode output does"
        if _softcode == 1:
            self._data.custom.trials.early_withdrawal_timer_start = time.time()
        elif _softcode == 2:
            if (time.time() -
                self._data.custom.trials.early_withdrawal_timer_start >
                self._task_parameters.timeout_early_withdrawal):

                self._bpod.trigger_event_by_name(event_name = 'SoftCode1',
                                                 event_data = None)

    def run(self):
        "Runs the protocol"
        i_trial = 0
        self._data.custom.assign_future_trials(START_FROM,NUM_TRIALS_TO_GENERATE)
        self._data.custom.generate_next_trial(i_trial)
        self._bpod.softcode_handler_function = self.my_softcode_handler
        while True:
            logger.error('Before StateMatrix()')
            sma = StateMatrix(
                self._bpod, self._task_parameters, self._data, i_trial)
            logger.error('Before send_state_machine()')
            self._bpod.send_state_machine(sma)
            logger.error('Before run_state_machine()')
            if not self._bpod.run_state_machine(sma):
                break
            self._data.custom.update(i_trial)
            i_trial += 1
