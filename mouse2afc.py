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
from utils import ControlledRandom
from utils import iff
from utils import betarnd
from utils import rand
from utils import randsample

logger = logging.getLogger(__name__)


class Mouse2AFCError(Exception):
    pass


def error(message):
    logger.error(message)
    raise Mouse2AFCError(message)

NumTrialsToGenerate = 1
StartFrom = 1

class Mouse2AFC:
    def __init__(self, bpod, config_file=None):
        self._bpod = bpod
        self._task_parameters = TaskParameters(
            file_=config_file).task_parameters
        self._data = Data(self._bpod.session, self._task_parameters)

    def _assign_future_trials(self):
        is_left_rewarded = ControlledRandom((1 - self._task_parameters.LeftBias),NumTrialsToGenerate)
        StartFrom = 1
        lastidx = StartFrom
        for a in range(NumTrialsToGenerate-1): 
            #If it's a fifty-fifty trial, then place stimulus in the middle
            if rand(1,1) < self._task_parameters.Percent50Fifty and (lastidx + a) > self._task_parameters.StartEasyTrials:
                StimulusOmega = .5
            else:
                gui_ssc = self._task_parameters.StimulusSelectionCriteria
                beta_dist = self._task_parameters.BetaDistAlphaNBeta
                if gui_ssc == StimulusSelectionCriteria.BetaDistribution:
                    # Divide beta by 4 if we are in an easy trial
                    BetaDiv = iff((lastidx+a) <= self._task_parameters.StartEasyTrials,4,1)
                    StimulusOmega = betarnd(beta_dist/BetaDiv,beta_dist/BetaDiv,1)
                    StimulusOmega = iff(StimulusOmega < 0.1, 0.1, StimulusOmega)
                    StimulusOmega = iff(StimulusOmega > 0.9,0.9,StimulusOmega)
                elif gui_ssc == StimulusSelectionCriteria.DiscretePairs:
                    if (lastidx+a) <= self._task_parameters.StartEasyTrialsa:
                        omega_prob = self._task_parameters.OmegaTable.columns.OmegaProb
                        index = next(omega_prob.index(prob)
                                    for prob in omega_prob if prob > 0)
                        StimulusOmega = self._task_parameters.OmegaTable.columns.Omega[
                            index] / 100
                    else:
                        #Choose a value randomly given the each value probability
                        StimulusOmega = randsample(self._task_parameters.OmegaTable.columns.Omega,1,1,omega_prob/100)
                else:
                    error('Unexpected StimulusSelectionCriteria')

                if (is_left_rewarded(a+1) and StimulusOmega < 0.5) or (not is_left_rewarded(a+1) and StimulusOmega >= 0.5):
                    StimulusOmega = -StimulusOmega + 1
            
            Trial = self._data.Custom.Trials[lastidx+a]
            Trial.StimulusOmega = StimulusOmega
            if StimulusOmega != 0.5:
                Trial.LeftRewarded = StimulusOmega > 0.5
            else:
                Trial.LeftRewarded = rand() < .5
            self._data.Custom.Trials[lastidx+a] = Trial
            # TODO relocate the following chunk of code
            self._data.Custom.StimulusOmega[a] = intensity
            task_experiment_type = self._task_parameters.ExperimentType
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
        StartFrom = StartFrom + NumTrialsToGenerate

    def _set_current_stimulus(self):
        # Set current stimulus for next trial - set between -100 to +100
        self._task_parameters.CurrentStim = (self._data.Custom.Trials.DV[0] + (
            int(self._data.Custom.Trials.DV[0] > 0) or -1)) / 0.02

    def run(self):
        self._assign_future_trials()
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
