import logging

from data import Data
from state_matrix import StateMatrix
from task_parameters import TaskParameters

from definitions.constant import Constant as Const
from definitions.stimulus_selection_criteria \
    import StimulusSelectionCriteria
from definitions.experiment import ExperimentType

from utils import CalcAudClickTrain
from utils import CalcDotsCoherence
from utils import CalcGratingOrientation
from utils import CalcLightIntensity
from utils import betarnd
from utils import rand

logger = logging.getLogger(__name__)


class Mouse2AFCError(Exception):
    pass


def error(message):
    logger.error(message)
    raise Mouse2AFCError(message)


class Mouse2AFC:
    def __init__(self, bpod):
        self._bpod = bpod
        self._task_parameters = TaskParameters()
        self._data = Data(self._bpod.session, self._task_parameters)

    def _set_custom_data(self):
        for a in range(Const.NUM_EASY_TRIALS):
            gui_ssc = self._task_parameters.GUI.StimulusSelectionCriteria
            if gui_ssc == StimulusSelectionCriteria.BetaDistribution:
                # This random value is between 0 and 1, the beta distribution
                # parameters makes it very likely to very close to zero or very
                # close to 1.
                beta_dist_param = self._task_parameters.BetaDistAlphaNBeta / 4
                self._data.Custom.StimulusOmega[a] = [
                    betarnd(beta_dist_param, beta_dist_param)]
            elif gui_ssc == StimulusSelectionCriteria.DiscretePairs:
                omega_prob = self._task_parameters.GUI.OmegaTable.OmegaProb
                index = next(omega_prob.index(prob)
                             for prob in omega_prob if prob > 0)
                intensity = self._task_parameters.GUI.OmegaTable.Omega[
                    index] / 100
            else:
                error('Unexpected StimulusSelectionCriteria')
            # Randomly choose right or left
            is_left_rewarded = bool(rand(1, 1) >= 0.5)
            # In case of beta distribution, our distribution is symmetric,
            # so prob < 0.5 is == prob > 0.5, so we can just pick the value
            # that corrects the bias
            if not is_left_rewarded and intensity >= 0.5:
                intensity = 1 - intensity
            # BUG: Figure out whether this or the previous assignment
            # is the correct one
            self._data.Custom.StimulusOmega[a] = intensity
            task_experiment_type = self._task_parameters.GUI.ExperimentType
            if task_experiment_type == ExperimentType.Auditory:
                dv = CalcAudClickTrain(self._data, a)
            elif task_experiment_type == ExperimentType.LightIntensity:
                dv = CalcLightIntensity(self._data, a)
            elif task_experiment_type == ExperimentType.GratingOrientation:
                dv = CalcGratingOrientation(self._data, a)
            elif task_experiment_type == ExperimentType.RandomDots:
                dv = CalcDotsCoherence(self._data, a)
            else:
                error('Unexpected ExperimentType')
            if dv > 0:
                self._data.Custom.LeftRewarded[a] = True
            elif dv < 0:
                self._data.Custom.LeftRewarded[a] = False
            else:
                self._data.Custom.LeftRewarded[a] = bool(
                    rand() < 0.5)  # It's equal distribution
            # cross - modality difficulty for plotting
            self._data.Custom.DV[a] = dv

    def _set_current_stimulus(self):
        # Set current stimulus for next trial - set between -100 to +100
        self._task_parameters.GUI.CurrentStim = (self._data.Custom.DV[0] + (
            int(self._data.Custom.DV[0] > 0) or -1)) / 0.02

    def run(self):
        self._set_custom_data()
        self._set_current_stimulus()
        i_trial = 0
        while True:
            logger.error('Before StateMatrix()')
            sma = StateMatrix(
                self._bpod, self._task_parameters, self._data, i_trial)
            logger.error('Before send_state_machine()')
            self._bpod.send_state_machine(sma)
            logger.error('Before run_state_machine()')
            self._bpod.run_state_machine(sma)
            self._data.Custom.update(i_trial)
