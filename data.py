import logging
import random
import time

from collections import OrderedDict

from definitions.constant import Constant as Const
from definitions.experiment import ExperimentType
from definitions.matrix_state import MatrixState
from definitions.feedback_delay_selection import FeedbackDelaySelection
from definitions.min_sample_type import MinSampleType
from definitions.stimulus_selection_criteria \
    import StimulusSelectionCriteria
from utils import betarnd
from utils import iff
from utils import rand
from utils import randi
from utils import randsample
from utils import round
from utils import floor
from utils import random_unif
from utils import diff
from utils import GetCatchStimIdx
from utils import TruncatedExponential
from utils import CalcAudClickTrain
from utils import CalcLightIntensity
from utils import CalcGratingOrientation
from utils import CalcDotsCoherence

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

NUM_OF_TRIALS = 800 #This can be changed. 800 is arbitrary

def error(message):
    logger.error(message)
    raise DataError(message)


def warning(message):
    logger.warning(message)


def datalist(value=0, size=NUM_OF_TRIALS):
    return [value] * size


class DataError(Exception):
    pass


class RawData:
    def __init__(self, session):
        self._session = session
        self.StateMachineErrorCodes = {}

    def StatesVisitedNames(self, trial_num):
        return [state.state_name for state in self._session.trials[
            trial_num].states_occurrences]

    def StatesVisitedTimes(self, trial_num):
        res_dict = OrderedDict()
        for state in self._session.trials[trial_num].states_occurrences:
            state_name = state.state_name
            res_dict[state_name] = res_dict.get(state_name, [])
            res_dict[state_name].append(
                (state.start_timestamp, state.end_timestamp))
        return res_dict

    def OriginalStateNamesByNumber(self, trial_num):
        return self._session.trials[trial_num].sma.state_names

    def OriginalStateData(self, trial_num):
        return self._session.trials[trial_num].states

    def OriginalEventData(self, trial_num):
        return self._session.trials[trial_num].events_occurrences

    def OriginalStateTimestamps(self, trial_num):
        return self._session.trials[trial_num].state_timestamps

    def OriginalEventTimestamps(self, trial_num):
        return self._sessions.trials[trial_num].event_timestamps


class CustomData:

    _DEFAULT_CATCH_COUNT_LEN = 21

    def __init__(self, task_parameters, Timer, RawData):
        self.task_parameters = task_parameters
        self.drawParams = drawParams()
        self.Timer = Timer
        self.RawData = RawData
        self.Trials = trials(task_parameters)
        self.DVsAlreadyGenerated = 0

    def assign_future_trials(self,StartFrom,NumTrialsToGenerate):
        is_left_rewarded = ControlledRandom((1 - self.task_parameters.LeftBias),NumTrialsToGenerate)
        lastidx = StartFrom
        for a in range(NumTrialsToGenerate):
            #If it's a fifty-fifty trial, then place stimulus in the middle
            if rand(1,1) < self.task_parameters.Percent50Fifty and (lastidx+a) > self.task_parameters.StartEasyTrials:
                StimulusOmega = .5
            else:
                gui_ssc = self.task_parameters.StimulusSelectionCriteria
                beta_dist = self.task_parameters.BetaDistAlphaNBeta
                if gui_ssc == StimulusSelectionCriteria.BetaDistribution:
                    # Divide beta by 4 if we are in an easy trial
                    BetaDiv = iff((lastidx+a) <= self.task_parameters.StartEasyTrials,4,1)
                    StimulusOmega = betarnd(beta_dist/BetaDiv,beta_dist/BetaDiv,1)
                    StimulusOmega = iff(StimulusOmega < 0.1, 0.1, StimulusOmega)
                    StimulusOmega = iff(StimulusOmega > 0.9,0.9,StimulusOmega)
                elif gui_ssc == StimulusSelectionCriteria.DiscretePairs:
                    omega_prob = self.task_parameters.OmegaTable.columns.OmegaProb
                    if (lastidx+a) <= self.task_parameters.StartEasyTrials:
                        index = next(omega_prob.index(prob)
                                    for prob in omega_prob if prob > 0)
                        StimulusOmega = self.task_parameters.OmegaTable.columns.Omega[
                            index] / 100
                    else:
                        #Choose a value randomly given the each value probability
                        StimulusOmega = randsample(self.task_parameters.OmegaTable.columns.Omega,1,1,omega_prob)/100
                else:
                    error('Unexpected StimulusSelectionCriteria')

                if (is_left_rewarded[a] and StimulusOmega < 0.5) or (not is_left_rewarded[a] and StimulusOmega >= 0.5):
                    StimulusOmega = -StimulusOmega + 1

            self.Trials.StimulusOmega[lastidx+a] = StimulusOmega
            if StimulusOmega != 0.5:
                self.Trials.LeftRewarded[lastidx+a] = StimulusOmega > 0.5
            else:
                self.Trials.LeftRewarded[lastidx+a] = rand() < .5
            
            if self.task_parameters.ExperimentType == \
                    ExperimentType.Auditory:
                DV = CalcAudClickTrain(lastidx + a)
            elif self.task_parameters.ExperimentType == \
                    ExperimentType.LightIntensity:
                DV = CalcLightIntensity(self, lastidx + a)
            elif self.task_parameters.ExperimentType == \
                    ExperimentType.GratingOrientation:
                DV = CalcGratingOrientation(lastidx + a)
            elif self.task_parameters.ExperimentType == \
                    ExperimentType.RandomDots:
                DV = CalcDotsCoherence(lastidx + a)
            else:
                error('Unexpected ExperimentType')
            if DV > 0:
                self.Trials.LeftRewarded[lastidx + a] = True
            elif DV < 0:
                self.Trials.LeftRewarded[lastidx + a] = False
            else:
                # It's equal distribution
                self.Trials.LeftRewarded[lastidx + a] = rand() < 0.5
            # cross-modality difficulty for plotting
            #  0 <= (left - right) / (left + right) <= 1
            self.Trials.DV[lastidx + a] = DV

        self.DVsAlreadyGenerated = StartFrom + NumTrialsToGenerate

    def update(self, i_trial):
        # Standard values

        # Stores which lateral port the animal poked into (if any)
        self.Trials.ChoiceLeft[i_trial] = None
        # Stores whether the animal poked into the correct port (if any)
        self.Trials.ChoiceCorrect[i_trial] = None
        # Signals whether confidence was used in this trial. Set to false if
        # lateral ports choice timed-out (i.e, MissedChoice(i) is true), it
        # also should be set to false (but not due to a bug) if the animal
        # poked the a lateral port but didn't complete the feedback period
        # (even with using grace).
        self.Trials.Feedback[i_trial] = True
        # How long the animal spent waiting for the reward (whether in correct
        # or in incorrect ports)
        self.Trials.FeedbackTime[i_trial] = None
        # Signals whether the animal broke fixation during stimulus delay state
        self.Trials.FixBroke[i_trial] = False
        # Signals whether the animal broke fixation during sampling but before
        # min-sampling ends
        self.Trials.EarlyWithdrawal[i_trial] = False
        # Signals whether the animal correctly finished min-sampling but failed
        # to poke any of the lateral ports within ChoiceDeadLine period
        self.Trials.MissedChoice[i_trial] = False
        # How long the animal remained fixated in center poke
        self.Trials.FixDur[i_trial] = None
        # How long between sample end and making a choice (timeout-choice
        # trials are excluded)
        self.Trials.MT[i_trial] = None
        # How long the animal sampled. If RewardAfterMinSampling is enabled and
        # animal completed min sampling, then it's equal to MinSample time,
        # otherwise it's how long the animal remained fixated in center-port
        # until it either poked-out or the max allowed sampling time was
        # reached.
        self.Trials.ST[i_trial] = None
        # Signals whether a reward was given to the animal (it also includes
        # if the animal poked into the correct reward port but poked out
        # afterwards and didn't receive a reward, due to 'RewardGrace' being
        # counted as reward).
        self.Trials.Rewarded[i_trial] = False
        # Signals whether a center-port reward was given after min-sampling
        # ends.
        self.Trials.RewardAfterMinSampling[i_trial] = False
        # Tracks the amount of water the animal received up tp this point
        # TODO: Check if RewardReceivedTotal is needed and calculate it using
        # CalcRewObtained() function.
        # We will updated later
        self.Trials.RewardReceivedTotal[i_trial + 1] = 0

        self.Trials.TrialNumber[i_trial] = i_trial

        self.Timer.customInitialize[i_trial] = time.time()

        # Checking states and rewriting standard

        # Extract the states that were used in the last trial
        statesVisitedThisTrialNames = self.RawData.StatesVisitedNames(i_trial)
        statesVisitedThisTrialTimes = self.RawData.StatesVisitedTimes(i_trial)
        if str(MatrixState.WaitForStimulus) in statesVisitedThisTrialNames:
            lastWaitForStimulusStateTimes = statesVisitedThisTrialTimes[
                str(MatrixState.WaitForStimulus)][-1]
            lastTriggerWaitForStimulusStateTimes = statesVisitedThisTrialTimes[
                str(MatrixState.TriggerWaitForStimulus)][-1]
            self.Trials.FixDur[i_trial] = lastWaitForStimulusStateTimes[1] - \
                lastWaitForStimulusStateTimes[0] + \
                lastTriggerWaitForStimulusStateTimes[1] - \
                lastTriggerWaitForStimulusStateTimes[0]
        if str(MatrixState.stimulus_delivery) in statesVisitedThisTrialNames:
            stimulus_deliveryStateTimes = statesVisitedThisTrialTimes[
                str(MatrixState.stimulus_delivery)]
            if self.task_parameters.RewardAfterMinSampling:
                self.Trials.ST[i_trial] = diff(stimulus_deliveryStateTimes)
            else:
                # 'CenterPortRewardDelivery' state would exist even if no
                # 'RewardAfterMinSampling' is active, in such case it means
                # that min sampling is done and we are in the optional
                # sampling stage.
                if str(MatrixState.CenterPortRewardDelivery) in \
                        statesVisitedThisTrialNames and \
                        self.task_parameters.StimulusTime > \
                        self.task_parameters.MinSample:
                    CenterPortRewardDeliveryStateTimes = \
                        statesVisitedThisTrialTimes[
                            str(MatrixState.CenterPortRewardDelivery)]
                    self.ST[i_trial] = [
                        CenterPortRewardDeliveryStateTimes[0][
                            1] - stimulus_deliveryStateTimes[0][0]
                    ]
                else:
                    # This covers early_withdrawal
                    self.ST[i_trial] = diff(stimulus_deliveryStateTimes)

        if str(MatrixState.WaitForChoice) in statesVisitedThisTrialNames and \
            str(MatrixState.timeOut_missed_choice) not in \
                statesVisitedThisTrialNames:
            WaitForChoiceStateTimes = statesVisitedThisTrialTimes[
                str(MatrixState.WaitForChoice)]
            WaitForChoiceStateStartTimes = [
                start_time for start_time, end_time in WaitForChoiceStateTimes]
            # We might have more than multiple WaitForChoice if
            # HabituateIgnoreIncorrect is enabeld
            self.MT[-1] = diff(WaitForChoiceStateStartTimes[:2])

        # Extract trial outcome. Check first if it's a wrong choice or a
        # HabituateIgnoreIncorrect but first choice was wrong choice
        if str(MatrixState.WaitForPunishStart) in \
            statesVisitedThisTrialNames or \
           str(MatrixState.RegisterWrongWaitCorrect) in \
                statesVisitedThisTrialNames:
            self.Trials.ChoiceCorrect[i_trial] = False
            # Correct choice = left
            if self.Trials.LeftRewarded[i_trial]:
                self.Trials.ChoiceLeft[i_trial] = False  # Left not chosen
            else:
                self.Trials.ChoiceLeft[i_trial] = True
            # Feedback waiting time
            if str(MatrixState.WaitForPunish) in statesVisitedThisTrialNames:
                WaitForPunishStateTimes = statesVisitedThisTrialTimes[
                    str(MatrixState.WaitForPunish)]
                WaitForPunishStartStateTimes = statesVisitedThisTrialTimes[
                    str(MatrixState.WaitForPunishStart)]
                self.Trials.FeedbackTime[i_trial] = WaitForPunishStateTimes[
                    -1][1] - WaitForPunishStartStateTimes[0][0]
            else:  # It was a  RegisterWrongWaitCorrect state
                self.Trials.FeedbackTime[i_trial] = None
        # CorrectChoice
        elif str(MatrixState.WaitForRewardStart) in \
                statesVisitedThisTrialNames:
            self.Trials.ChoiceCorrect[i_trial] = True
            if self.Trials.CatchTrial[i_trial]:
                catch_stim_idx = GetCatchStimIdx(
                    self.Trials.StimulusOmega[i_trial])
                # Lookup the stimulus probability and increase by its
                # 1/frequency.
                stim_val = self.StimulusOmega[i_trial] * 100
                if stim_val < 50:
                    stim_val = 100 - stim_val
                stim_prob = self.task_parameters.OmegaTable.columns.OmegaProb[
                    self.task_parameters.OmegaTable.columns.Omega.index(
                        stim_val)]
                sum_all_prob = sum(
                    self.task_parameters.OmegaTable.columns.OmegaProb)
                stim_prob = (1 + sum_all_prob - stim_prob) / sum_all_prob
                self.Trials.CatchCount[catch_stim_idx] += stim_prob
                self.Trials.LastSuccessCatchTial = i_trial
            # Feedback waiting time
            if str(MatrixState.WaitForReward) in statesVisitedThisTrialNames:
                WaitForRewardStateTimes = statesVisitedThisTrialTimes[
                    str(MatrixState.WaitForReward)]
                WaitForRewardStartStateTimes = statesVisitedThisTrialTimes[
                    str(MatrixState.WaitForRewardStart)]
                self.Trials.FeedbackTime[i_trial] = WaitForRewardStateTimes[
                    -1][1] - WaitForRewardStartStateTimes[0][0]
                # Correct choice = left
                if self.Trials.LeftRewarded[i_trial]:
                    self.Trials.ChoiceLeft[i_trial] = True  # Left chosen
                else:
                    self.Trials.ChoiceLeft[i_trial] = False
            else:
                warning("'WaitForReward' state should always appear"
                        " if 'WaitForRewardStart' was initiated")
        elif str(MatrixState.broke_fixation) in statesVisitedThisTrialNames:
            self.Trials.FixBroke[i_trial] = True
        elif str(MatrixState.early_withdrawal) in statesVisitedThisTrialNames:
            self.Trials.EarlyWithdrawal[i_trial] = True
        elif str(MatrixState.timeOut_missed_choice) in \
                statesVisitedThisTrialNames:
            self.Trials.Feedback[i_trial] = False
            self.Trials.MissedChoice[i_trial] = True
        if str(MatrixState.timeOut_SkippedFeedback) in \
                statesVisitedThisTrialNames:
            self.Trials.Feedback[i_trial] = False
        if str(MatrixState.Reward) in statesVisitedThisTrialNames:
            self.Trials.Rewarded[i_trial] = True
            self.Trials.RewardReceivedTotal[i_trial] += \
                self.task_parameters.RewardAmount
        if str(MatrixState.CenterPortRewardDelivery) in \
                statesVisitedThisTrialNames and \
           self.task_parameters.RewardAfterMinSampling:
            self.Trials.RewardAfterMinSampling[i_trial] = True
            self.Trials.RewardReceivedTotal[i_trial] += \
                self.task_parameters.CenterPortRewAmount
        if str(MatrixState.WaitCenterPortOut) in statesVisitedThisTrialNames:
            WaitCenterPortOutStateTimes = statesVisitedThisTrialTimes[
                str(MatrixState.WaitCenterPortOut)]
            self.Trials.ReactionTime[i_trial] = diff(
                WaitCenterPortOutStateTimes)
        else:
            # Assign with -1 so we can differentiate it from None trials
            # where the state potentially existed but we didn't calculate it
            self.Trials.ReactionTime[i_trial] = -1
        # State-independent fields
        self.Trials.StimDelay[i_trial] = self.task_parameters.StimDelay
        self.Trials.FeedbackDelay[i_trial] = self.task_parameters.FeedbackDelay
        self.Trials.MinSample[i_trial] = self.task_parameters.MinSample
        self.Trials.RewardMagnitude[i_trial + 1] = [
            self.task_parameters.RewardAmount,
            self.task_parameters.RewardAmount]
        self.Trials.CenterPortRewAmount[
            i_trial + 1] = self.task_parameters.CenterPortRewAmount
        self.Trials.PreStimCntrReward[
            i_trial + 1] = self.task_parameters.PreStimDelayCntrReward
        self.Timer.customExtractData[i_trial] = time.time()

        # IF we are running grating experiments,
        # add the grating orientation that was used
        if self.task_parameters.ExperimentType == \
                ExperimentType.GratingOrientation:
            self.GratingOrientation[
                i_trial] = self.drawParams.gratingOrientation

        # Updating Delays
        # stimulus delay
        if self.task_parameters.StimDelayAutoincrement:
            if self.FixBroke[i_trial]:
                self.task_parameters.StimDelay = max(
                    self.task_parameters.StimDelayMin,
                    min(self.task_parameters.StimDelayMax,
                        self.StimDelay[
                            i_trial] - self.task_parameters.StimDelayDecr))
            else:
                self.task_parameters.StimDelay = min(
                    self.task_parameters.StimDelayMax,
                    max(self.task_parameters.StimDelayMin,
                        self.StimDelay[
                            i_trial] + self.task_parameters.StimDelayIncr))
        else:
            if not self.Trials.FixBroke[i_trial]:
                self.task_parameters.StimDelay = random_unif(
                    self.task_parameters.StimDelayMin,
                    self.task_parameters.StimDelayMax)
            else:
                self.task_parameters.StimDelay = self.StimDelay[i_trial]
        self.Timer.customStimDelay[i_trial] = time.time()

        # min sampling time
        if i_trial > self.task_parameters.StartEasyTrials:
            if self.task_parameters.MinSampleType == MinSampleType.FixMin:
                self.task_parameters.MinSample = \
                    self.task_parameters.MinSampleMin
            elif self.task_parameters.MinSampleType == \
                    MinSampleType.AutoIncr:
                # Check if animal completed pre-stimulus delay successfully
                if not self.Trials.FixBroke[i_trial]:
                    if self.Trials.Rewarded[i_trial]:
                        min_sample_incremented = self.Trials.MinSample[
                            i_trial] + self.task_parameters.MinSampleIncr
                        self.task_parameters.MinSample = min(
                            self.task_parameters.MinSampleMax,
                            max(self.task_parameters.MinSampleMin,
                                min_sample_incremented))
                    elif self.Trials.EarlyWithdrawal[i_trial]:
                        min_sample_decremented = self.MinSample[
                            i_trial] - self.task_parameters.MinSampleDecr
                        self.task_parameters.MinSample = max(
                            self.task_parameters.MinSampleMin,
                            min(self.task_parameters.MinSampleMax,
                                min_sample_decremented))
                else:
                    # Read new updated GUI values
                    self.task_parameters.MinSample = max(
                        self.task_parameters.MinSampleMin,
                        min(self.task_parameters.MinSampleMax,
                            self.MinSample[i_trial]))
            elif self.task_parameters.MinSampleType == \
                    MinSampleType.RandBetMinMax_DefIsMax:
                use_rand = rand(
                    1, 1) < self.task_parameters.MinSampleRandProb
                if not use_rand:
                    self.task_parameters.MinSample = \
                        self.task_parameters.MinSampleMax
                else:
                    min_sample_difference = \
                        self.task_parameters.MinSampleMax - \
                        self.task_parameters.MinSampleMin
                    self.task_parameters.MinSample = \
                        min_sample_difference * \
                        rand(1, 1) + self.task_parameters.MinSampleMin
            elif MinSampleType.RandNumIntervalsMinMax_DefIsMax:
                use_rand = rand(
                    1, 1) < self.task_parameters.MinSampleRandProb
                if not use_rand:
                    self.task_parameters.MinSample = \
                        self.task_parameters.MinSampleMax
                else:
                    self.task_parameters.MinSampleNumInterval = round(
                        self.task_parameters.MinSampleNumInterval)
                    if self.task_parameters.MinSampleNumInterval == 0 or \
                       self.task_parameters.MinSampleNumInterval == 1:
                        self.task_parameters.MinSample = \
                            self.task_parameters.MinSampleMin
                    else:
                        min_sample_difference = \
                            self.task_parameters.MinSampleMax - \
                            self.task_parameters.MinSampleMin
                        step = min_sample_difference / (
                            self.task_parameters.MinSampleNumInterval - 1)
                        intervals = list(range(
                            self.task_parameters.MinSampleMin,
                            self.task_parameters.MinSampleMax + 1,
                            step))
                        intervals_idx = randi(
                            1, self.task_parameters.MinSampleNumInterval)
                        print("Intervals:")  # disp("Intervals:");
                        print(intervals)  # disp(intervals)
                        self.task_parameters.MinSample = intervals[
                            intervals_idx]
            else:
                error('Unexpected MinSampleType value')
        self.Timer.customMinSampling[i_trial] = time.time()

        # feedback delay
        if self.task_parameters.FeedbackDelaySelection == \
                FeedbackDelaySelection.none:
            self.task_parameters.FeedbackDelay = 0
        elif self.task_parameters.FeedbackDelaySelection == \
                FeedbackDelaySelection.AutoIncr:
            # if no feedback was not completed then use the last value unless
            # then decrement the feedback.
            # Do we consider the case where 'broke_fixation' or
            # 'early_withdrawal' terminated early the trial?
            if not self.Feedback[i_trial]:
                feedback_delay_decremented = self.FeedbackDelay[
                    i_trial] - self.task_parameters.FeedbackDelayDecr
                self.task_parameters.FeedbackDelay = max(
                    self.task_parameters.FeedbackDelayMin,
                    min(self.task_parameters.FeedbackDelayMax,
                        feedback_delay_decremented))
            else:
                # Increase the feedback if the feedback was successfully
                # completed in the last trial, or use the the GUI value that
                # the user updated if needed.
                # Do we also here consider the case where 'broke_fixation' or
                # 'early_withdrawal' terminated early the trial?
                feedback_delay_incremented = self.FeedbackDelay[
                    i_trial] + self.task_parameters.FeedbackDelayIncr
                self.task_parameters.FeedbackDelay = min(
                    self.task_parameters.FeedbackDelayMax,
                    max(self.task_parameters.FeedbackDelayMin,
                        feedback_delay_incremented))
        elif FeedbackDelaySelection.TruncExp:
            self.task_parameters.FeedbackDelay = TruncatedExponential(
                self.task_parameters.FeedbackDelayMin,
                self.task_parameters.FeedbackDelayMax,
                self.task_parameters.FeedbackDelayTau)
        elif FeedbackDelaySelection.Fix:
            #     ATTEMPT TO GRAY OUT FIELDS
            if self.task_parametersMeta.FeedbackDelay.Style != 'edit':
                self.task_parametersMeta.FeedbackDelay.Style = 'edit'
            self.task_parameters.FeedbackDelay = \
                self.task_parameters.FeedbackDelayMax
        else:
            error('Unexpected FeedbackDelaySelection value')
        self.Timer.customFeedbackDelay[i_trial] = time.time()

        # Drawing future trials

        # Calculate bias
        # Consider bias only on the last 8 trials/
        # indicesRwdLi = find(self.Rewarded,8,'last');
        # if length(indicesRwdLi) ~= 0
        #   indicesRwd = indicesRwdLi(1);
        # else
        #   indicesRwd = 1;
        # end
        LAST_TRIALS = 20
        indicesRwd = iff(i_trial > LAST_TRIALS, i_trial - LAST_TRIALS, 1)
        # ndxRewd = self.Rewarded(indicesRwd:i_trial);
        choice_correct_slice = self.Trials.ChoiceCorrect[
            indicesRwd: i_trial + 1]
        choice_left_slice = self.Trials.ChoiceLeft[indicesRwd: i_trial + 1]
        left_rewarded_slice = self.Trials.LeftRewarded[indicesRwd: i_trial + 1]
        ndxLeftRewd = [choice_c and choice_l for choice_c, choice_l in zip(
            choice_correct_slice, choice_left_slice)]
        ndxLeftRewDone = [l_rewarded and choice_l is not None
                          for l_rewarded, choice_l in zip(
                              left_rewarded_slice, choice_left_slice)]
        ndxRightRewd = [choice_c and not choice_l
                        for choice_c, choice_l in zip(
                            choice_correct_slice, choice_left_slice)]
        ndxRightRewDone = [not l_rewarded and choice_l is not None
                           for l_rewarded, choice_l in zip(
                               left_rewarded_slice, choice_left_slice)]
        if not any(ndxLeftRewDone):
            # Since we don't have trials on this side, then measure by how good
            # the animals was performing on the other side. If it did bad on
            # the side then then consider this side performance to be good so
            # it'd still get more trials on the other side.
            PerfL = 1 - (sum(ndxRightRewd) / (LAST_TRIALS * 2))
        else:
            PerfL = sum(ndxLeftRewd) / sum(ndxLeftRewDone)
        if not any(ndxRightRewDone):
            PerfR = 1 - (sum(ndxLeftRewd) / (LAST_TRIALS * 2))
        else:
            PerfR = sum(ndxRightRewd) / sum(ndxRightRewDone)
        self.task_parameters.CalcLeftBias = (PerfL - PerfR) / 2 + 0.5

        choiceMadeTrials = [
            choice_c is not None for choice_c in self.Trials.ChoiceCorrect]
        rewardedTrialsCount = sum([r is True for r in self.Trials.Rewarded])
        lengthChoiceMadeTrials = len(choiceMadeTrials)
        if lengthChoiceMadeTrials >= 1:
            performance = rewardedTrialsCount / lengthChoiceMadeTrials
            self.task_parameters.Performance = [
                f'{performance * 100:.2f}', '#/',
                str(lengthChoiceMadeTrials), 'T']
            performance = rewardedTrialsCount / (i_trial + 1)
            self.task_parameters.AllPerformance = [
                f'{performance * 100:.2f}', '#/', str(i_trial + 1), 'T']
            NUM_LAST_TRIALS = 20
            if i_trial > NUM_LAST_TRIALS:
                if lengthChoiceMadeTrials > NUM_LAST_TRIALS:
                    rewardedTrials_ = choiceMadeTrials[
                        lengthChoiceMadeTrials - NUM_LAST_TRIALS + 1:
                        lengthChoiceMadeTrials + 1]
                    performance = sum(rewardedTrials_) / NUM_LAST_TRIALS
                    self.task_parameters.Performance = [
                        self.task_parameters.Performance, ' - ',
                        f'{performance * 100:.2f}', '#/',
                        str(NUM_LAST_TRIALS), 'T']
                rewardedTrialsCount = sum(self.Trials.Rewarded[
                    i_trial - NUM_LAST_TRIALS + 1: i_trial + 1])
                performance = rewardedTrialsCount / NUM_LAST_TRIALS
                self.task_parameters.AllPerformance = [
                    self.task_parameters.AllPerformance, ' - ',
                    f'{performance * 100:.2f}', '#/', str(NUM_LAST_TRIALS),
                    'T']
        self.Timer.customCalcBias[i_trial] = time.time()

        # Create future trials
        # Check if its time to generate more future trials
        if i_trial+1 >= self.DVsAlreadyGenerated:
            # Do bias correction only if we have enough trials
            # sum(ndxRewd) > Const.BIAS_CORRECT_MIN_RWD_TRIALS
            if self.task_parameters.CorrectBias and i_trial > 7:
                LeftBias = self.task_parameters.CalcLeftBias
                # if LeftBias < 0.2 || LeftBias > 0.8 # Bias is too much,
                # swing it all the way to the other side
                # LeftBias = round(LeftBias);
                # else
                if 0.45 <= LeftBias and LeftBias <= 0.55:
                    LeftBias = 0.5
                if LeftBias is None:
                    print(f'Left bias is None.')
                    LeftBias = 0.5
            else:
                LeftBias = self.task_parameters.LeftBias
            self.Timer.customAdjustBias[i_trial] = time.time()

            # Adjustment of P(Omega) to make sure that sum(P(Omega))=1
            if self.task_parameters.StimulusSelectionCriteria != \
                    StimulusSelectionCriteria.BetaDistribution:
                omega_prob_sum = sum(
                    self.task_parameters.OmegaTable.columns.OmegaProb)
                # Avoid having no probability and avoid dividing by zero
                if omega_prob_sum == 0:
                    self.task_parameters.OmegaTable.columns.OmegaProb = [1] * \
                        len(self.task_parameters.OmegaTable.columns.OmegaProb)
                self.task_parameters.OmegaTable.columns.OmegaProb = [
                    omega_prob / omega_prob_sum
                    for omega_prob
                    in self.task_parameters.OmegaTable.columns.OmegaProb
                ]
            self.Timer.customCalcOmega[i_trial] = time.time()
            self.assign_future_trials(i_trial+1,Const.PRE_GENERATE_TRIAL_COUNT)

            self.Timer.customGenNewTrials[i_trial] = time.time()
        else:
            self.Timer.customAdjustBias[i_trial] = 0
            self.Timer.customCalcOmega[i_trial] = 0
            self.Timer.customPrepNewTrials[i_trial] = 0
            self.Timer.customGenNewTrials[i_trial] = 0

        # Update RDK GUI
        self.task_parameters.OmegaTable.columns.RDK = [
            (value - 50) * 2
            for value in self.task_parameters.OmegaTable.columns.Omega
        ]
        # Set current stimulus for next trial
        DV = self.Trials.DV[i_trial + 1]
        if self.task_parameters.ExperimentType == \
                ExperimentType.RandomDots:
            self.task_parameters.CurrentStim = \
                f"{abs(DV / 0.01)}{iff(DV < 0, '# R cohr.', '# L cohr.')}"
        else:
            # Set between -100 to +100
            StimIntensity = f'{iff(DV > 0, (DV + 1) / 0.02, (DV - 1) / -0.02)}'
            self.task_parameters.CurrentStim = \
                f"{StimIntensity}{iff(DV < 0, '# R', '# L')}"

        self.Timer.customFinalizeUpdate[i_trial] = time.time()

        # determine if optogentics trial
        OptoEnabled = rand(1, 1) < self.task_parameters.OptoProb
        if i_trial < self.task_parameters.StartEasyTrials:
            OptoEnabled = False
        self.Trials.OptoEnabled[i_trial + 1] = OptoEnabled
        self.task_parameters.IsOptoTrial = iff(
            OptoEnabled, 'true', 'false')

        # determine if catch trial
        if i_trial < self.task_parameters.StartEasyTrials or \
                self.task_parameters.PercentCatch == 0:
            self.Trials.CatchTrial[i_trial + 1] = False
        else:
            every_n_trials = round(1 / self.task_parameters.PercentCatch)
            limit = round(every_n_trials * 0.2)
            lower_limit = every_n_trials - limit
            upper_limit = every_n_trials + limit
            if not self.Trials.Rewarded[i_trial] or i_trial + 1 < \
                    self.Trials.LastSuccessCatchTial + lower_limit:
                self.Trials.CatchTrial[i_trial + 1] = False
            elif i_trial + 1 < self.Trials.LastSuccessCatchTial + upper_limit:
                # TODO: If OmegaProb changed since last time, then redo it
                non_zero_prob = [
                    self.task_parameters.OmegaTable.Omega[i] / 100
                    for i, prob in enumerate(
                        self.task_parameters.OmegaTable.columns.OmegaProb)
                    if prob > 0]
                complement_non_zero_prob = [1 - prob for prob in non_zero_prob]
                inverse_non_zero_prob = non_zero_prob[::-1]
                active_stim_idxs = GetCatchStimIdx(
                    complement_non_zero_prob + inverse_non_zero_prob)
                cur_stim_idx = GetCatchStimIdx(
                    self.Trials.StimulusOmega[i_trial + 1])
                min_catch_counts = min(
                    self.Trials.CatchCount[i] for i in active_stim_idxs)
                min_catch_idxs = list(set(active_stim_idxs).intersection(
                    {i for i, cc in enumerate(
                        self.Trials.CatchCount)
                     if floor(cc) == min_catch_counts}))
                self.Trials.CatchTrial[
                    i_trial + 1] = cur_stim_idx in min_catch_idxs
            else:
                self.Trials.CatchTrial[i_trial + 1] = True
        # Create as char vector rather than string so that
        # GUI sync doesn't complain
        self.task_parameters.IsCatch = iff(
            self.Trials.CatchTrial[i_trial + 1], 'true', 'false')
        # Determine if Forced LED trial:
        if self.task_parameters.PortLEDtoCueReward:
            self.Trials.ForcedLEDTrial[i_trial + 1] = rand(1, 1) < \
                self.task_parameters.PercentForcedLEDTrial
        else:
            self.Trials.ForcedLEDTrial[i_trial + 1] = False
        self.Timer.customCatchNForceLed[i_trial] = time.time()


class TimerData:
    def __init__(self):
        self.StartNewIter = datalist()
        self.SyncGUI = datalist()
        self.BuildStateMatrix = datalist()
        self.SendStateMatrix = datalist()
        self.AppendData = datalist()
        self.HandlePause = datalist()
        self.UpdateCustomDataFields = datalist()
        self.SendPlotData = datalist()
        self.SaveData = datalist()
        self.CalculateTimeout = datalist()
        self.customExtractData = datalist()
        self.customAdjustBias = datalist()
        self.customCalcOmega = datalist()
        self.customInitialize = datalist()
        self.customFinalizeUpdate = datalist()
        self.customCatchNForceLed = datalist()
        self.customStimDelay = datalist()
        self.customMinSampling = datalist()
        self.customFeedbackDelay = datalist()
        self.customCalcBias = datalist()
        self.customPrepNewTrials = datalist()
        self.customGenNewTrials = datalist()


class drawParams:
    def __init__(self):
        self.StimType = None
        self.GratingOrientation = None
        self.NumCycles = None
        self.CyclesPerSecondDrift = None
        self.Phase = None
        self.GaborSizeFactor = None
        self.GaussianFilterRatio = None
        self.CenterX = None
        self.CenterY = None
        self.ApertureSizeWidth = None
        self.ApertureSizeHeight = None
        self.DrawRatio = None
        self.MainDirection = None
        self.DotSpeed = None
        self.DotLifetimeSecs = None
        self.Coherence = None
        self.ScreenWidthCm = None
        self.ScreenDistCm = None
        self.DotSizeInDegs = None

class trials:

    _DEFAULT_CATCH_COUNT_LEN = 21
    def __init__(self,task_parameters):
        self.task_parameters = task_parameters
        self.ChoiceLeft = datalist(False)
        self.ChoiceCorrect = datalist(False)
        self.Feedback = datalist(False)
        self.FeedbackTime = datalist(False)
        self.FeedbackDelay = datalist(None)
        self.FixBroke = datalist(False)
        self.EarlyWithdrawal = datalist(False)
        self.MissedChoice = datalist(False)
        self.FixDur = datalist(None)
        self.MT = datalist(None)
        self.CatchTrial = datalist(False)
        self.ST = datalist(None)
        self.OptoEnabled = datalist(False)
        self.Rewarded = datalist(False)
        self.RewardAfterMinSampling = datalist(False)
        self.PreStimCounterReward = datalist(None)
        self.PreStimCntrReward = datalist(size=NUM_OF_TRIALS + 1)
        self.MinSample = datalist()
        self.LightIntensityLeft = datalist()
        self.LightIntensityRight = datalist()
        self.GratingOrientation = datalist()
        self.RewardMagnitude = datalist([
            self.task_parameters.RewardAmount,
            self.task_parameters.RewardAmount
        ])
        self.RewardReceivedTotal = datalist(size=NUM_OF_TRIALS + 1)
        self.ReactionTime = datalist()
        self.CenterPortRewAmount = datalist(
            self.task_parameters.CenterPortRewAmount)
        self.TrialNumber = datalist()
        self.ForcedLEDTrial = datalist(False)
        self.CatchCount = datalist(size=self._DEFAULT_CATCH_COUNT_LEN)
        self.LastSuccessCatchTrial = True
        self.StimulusOmega = datalist()
        self.StimDelay = datalist()
        self.LeftRewarded = datalist(None)
        self.DV = datalist()
        self.TrialStartSysTime = datalist(None)
        self.DotsCoherence = datalist()

class Data:
    def __init__(self, session, task_parameters):
        self.task_parameters = task_parameters
        self.RawData = RawData(session)
        self.Timer = TimerData()
        self.Custom = CustomData(task_parameters, self.Timer, self.RawData)
        self.TrialStartTimestamp = datalist()
        self.TrialEndTimestamp = datalist()
        self.SettingsFile = None
        self.dots_mapped_file = None
