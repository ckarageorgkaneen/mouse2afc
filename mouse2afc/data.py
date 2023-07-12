import logging
import time

from collections import OrderedDict

from numpy import arange

from mouse2afc.definitions.constant import Constant as Const
from mouse2afc.definitions.experiment import ExperimentType
from mouse2afc.definitions.matrix_state import MatrixState
from mouse2afc.definitions.feedback_delay_selection import FeedbackDelaySelection
from mouse2afc.definitions.min_sample_type import MinSampleType
from mouse2afc.definitions.stimulus_selection_criteria \
    import StimulusSelectionCriteria
from  mouse2afc.utils import betarnd
from  mouse2afc.utils import iff
from  mouse2afc.utils import rand
from  mouse2afc.utils import randi
from  mouse2afc.utils import randsample
from  mouse2afc.utils import round
from  mouse2afc.utils import floor
from  mouse2afc.utils import random_unif
from  mouse2afc.utils import diff
from  mouse2afc.utils import get_catch_stim_idx
from  mouse2afc.utils import truncated_exponential
from  mouse2afc.utils import calc_aud_click_train
from  mouse2afc.utils import calc_light_intensity
from  mouse2afc.utils import calc_grating_orientation
from  mouse2afc.utils import calc_dots_coherence
from  mouse2afc.utils import controlled_random
from  mouse2afc.utils import isnan

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
        self.state_machine_error_codes = {}

    def states_visited_names(self, trial_num):
        return [state.state_name for state in self._session.trials[
            trial_num].states_occurrences if not isnan(state.host_timestamp) ]

    def states_visited_times(self, trial_num):
        res_dict = OrderedDict()
        for state in self._session.trials[trial_num].states_occurrences:
            state_name = state.state_name
            res_dict[state_name] = res_dict.get(state_name, [])
            res_dict[state_name].append(
                (state.start_timestamp, state.end_timestamp))
        return res_dict

    def original_state_names_by_number(self, trial_num):
        return self._session.trials[trial_num].sma.state_names

    def original_state_data(self, trial_num):
        return self._session.trials[trial_num].states

    def orginal_event_data(self, trial_num):
        return self._session.trials[trial_num].events_occurrences

    def original_state_timestamps(self, trial_num):
        return self._session.trials[trial_num].state_timestamps

    def original_event_timestamps(self, trial_num):
        return self._session.trials[trial_num].event_timestamps


class CustomData:

    _DEFAULT_CATCH_COUNT_LEN = 21

    def __init__(self, task_parameters, timer, raw_data):
        self.task_parameters = task_parameters
        self.draw_params = DrawParams()
        self.timer = timer
        self.raw_data = raw_data
        self.trials = Trials(task_parameters)
        self.DVs_already_generated = 0

    def assign_future_trials(self,start_from,num_trials_to_generate):
        is_left_rewarded = controlled_random((1 -self.task_parameters.LeftBias),
                                              num_trials_to_generate)
        lastidx = start_from
        for a in range(num_trials_to_generate):
            #If it's a fifty-fifty trial, then place stimulus in the middle
            if (rand(1,1) < self.task_parameters.Percent50Fifty and
                (lastidx+a) > self.task_parameters.StartEasyTrials):
                stimulus_omega = .5
            else:
                gui_ssc = self.task_parameters.StimulusSelectionCriteria
                beta_dist = self.task_parameters.BetaDistAlphaNBeta
                if gui_ssc == StimulusSelectionCriteria.BetaDistribution:
                    # Divide beta by 4 if we are in an easy trial
                    beta_div = iff((lastidx+a) <= self.task_parameters.StartEasyTrials,4,1)
                    stimulus_omega = betarnd(beta_dist/beta_div,beta_dist/beta_div,1)
                    stimulus_omega = iff(stimulus_omega < 0.1, 0.1, stimulus_omega)
                    stimulus_omega = iff(stimulus_omega > 0.9,0.9,stimulus_omega)
                elif gui_ssc == StimulusSelectionCriteria.DiscretePairs:
                    omega_prob = self.task_parameters.OmegaTable.columns.OmegaProb
                    if (lastidx+a) <= self.task_parameters.StartEasyTrials:
                        index = next(omega_prob.index(prob)
                                    for prob in omega_prob if prob > 0)
                        stimulus_omega = self.task_parameters.OmegaTable.columns.Omega[
                            index] / 100
                    else:
                        #Choose a value randomly given the each value probability
                        stimulus_omega = (
                            (randsample
                             (self.task_parameters.OmegaTable.columns.Omega,
                              1,
                              1,
                              omega_prob)
                              / 100).tolist())[0]
                else:
                    error('Unexpected StimulusSelectionCriteria')

                if ((is_left_rewarded[a] and stimulus_omega < 0.5) or
                     (not is_left_rewarded[a] and stimulus_omega >= 0.5)):
                    stimulus_omega = -stimulus_omega + 1

            self.trials.stimulus_omega[lastidx+a] = stimulus_omega
            if stimulus_omega != 0.5:
                self.trials.left_rewarded[lastidx+a] = stimulus_omega > 0.5
            else:
                self.trials.left_rewarded[lastidx+a] = rand() < .5

        self.DVs_already_generated = start_from + num_trials_to_generate

    def update(self, i_trial):
        # Standard values

        # Stores which lateral port the animal poked into (if any)
        self.trials.choice_left[i_trial] = None
        # Stores whether the animal poked into the correct port (if any)
        self.trials.choice_correct[i_trial] = None
        # Signals whether confidence was used in this trial. Set to false if
        # lateral ports choice timed-out (i.e, missed_choice(i) is true), it
        # also should be set to false (but not due to a bug) if the animal
        # poked the a lateral port but didn't complete the feedback period
        # (even with using grace).
        self.trials.feedback[i_trial] = True
        # How long the animal spent waiting for the reward (whether in correct
        # or in incorrect ports)
        self.trials.feedback_time[i_trial] = None
        # Signals whether the animal broke fixation during stimulus delay state
        self.trials.fix_broke[i_trial] = False
        # Signals whether the animal broke fixation during sampling but before
        # min-sampling ends
        self.trials.early_withdrawal[i_trial] = False
        # Signals whether the animal correctly finished min-sampling but failed
        # to poke any of the lateral ports within ChoiceDeadLine period
        self.trials.missed_choice[i_trial] = False
        # How long the animal remained fixated in center poke
        self.trials.fix_dur[i_trial] = None
        # How long between sample end and making a choice (timeout-choice
        # trials are excluded)
        self.trials.mt[i_trial] = None
        # How long the animal sampled. If reward_after_min_sampling is enabled and
        # animal completed min sampling, then it's equal to min_sample time,
        # otherwise it's how long the animal remained fixated in center-port
        # until it either poked-out or the max allowed sampling time was
        # reached.
        self.trials.st[i_trial] = None
        # Signals whether a reward was given to the animal (it also includes
        # if the animal poked into the correct reward port but poked out
        # afterwards and didn't receive a reward, due to 'RewardGrace' being
        # counted as reward).
        self.trials.rewarded[i_trial] = False
        # Signals whether a center-port reward was given after min-sampling
        # ends.
        self.trials.reward_after_min_sampling[i_trial] = False
        # Tracks the amount of water the animal received up tp this point
        # TODO: Check if reward_received_total is needed and calculate it using
        # CalcRewObtained() function.
        # We will updated later
        self.trials.reward_received_total[i_trial + 1] = 0

        self.trials.trial_number[i_trial] = i_trial

        self.timer.custom_initialize[i_trial] = time.time()

        # Checking states and rewriting standard

        # Extract the states that were used in the last trial
        states_visited_this_trial_names = self.raw_data.states_visited_names(i_trial)
        states_visited_this_trial_times = self.raw_data.states_visited_times(i_trial)
        if str(MatrixState.WaitForStimulus) in states_visited_this_trial_names:
            last_wait_for_stimulus_states_times = states_visited_this_trial_times[
                str(MatrixState.WaitForStimulus)][-1]
            last_trigger_wait_for_stimulus_state_times = states_visited_this_trial_times[
                str(MatrixState.TriggerWaitForStimulus)][-1]
            self.trials.fix_dur[i_trial] = last_wait_for_stimulus_states_times[1] - \
                last_wait_for_stimulus_states_times[0] + \
                last_trigger_wait_for_stimulus_state_times[1] - \
                last_trigger_wait_for_stimulus_state_times[0]
        if str(MatrixState.stimulus_delivery) in states_visited_this_trial_names:
            stimulus_delivery_state_times = states_visited_this_trial_times[
                str(MatrixState.stimulus_delivery)]
            if self.task_parameters.RewardAfterMinSampling:
                self.trials.st[i_trial] = diff(stimulus_delivery_state_times)
            else:
                # 'CenterPortRewardDelivery' state would exist even if no
                # 'reward_after_min_sampling' is active, in such case it means
                # that min sampling is done and we are in the optional
                # sampling stage.
                if str(MatrixState.CenterPortRewardDelivery) in \
                        states_visited_this_trial_names and \
                        self.task_parameters.StimulusTime > \
                        self.task_parameters.MinSample:
                    center_port_reward_delivery_state_times = \
                        states_visited_this_trial_times[
                            str(MatrixState.CenterPortRewardDelivery)]
                    self.trials.st[i_trial] = [
                        center_port_reward_delivery_state_times[0][
                            1] - stimulus_delivery_state_times[0][0]
                    ]
                else:
                    # This covers early_withdrawal
                    self.trials.st[i_trial] = diff(stimulus_delivery_state_times)

        if str(MatrixState.WaitForChoice) in states_visited_this_trial_names and \
            str(MatrixState.timeOut_missed_choice) not in \
                states_visited_this_trial_names:
            wait_for_choice_state_times = states_visited_this_trial_times[
                str(MatrixState.WaitForChoice)]
            wait_for_choice_state_start_times = [
                start_time for start_time, end_time in wait_for_choice_state_times]
            # We might have more than multiple WaitForChoice if
            # HabituateIgnoreIncorrect is enabeld
            self.trials.mt[-1] = diff(wait_for_choice_state_start_times[:2])

        # Extract trial outcome. Check first if it's a wrong choice or a
        # HabituateIgnoreIncorrect but first choice was wrong choice
        if str(MatrixState.WaitForPunishStart) in \
            states_visited_this_trial_names or \
           str(MatrixState.RegisterWrongWaitCorrect) in \
                states_visited_this_trial_names:
            self.trials.choice_correct[i_trial] = False
            # Correct choice = left
            if self.trials.left_rewarded[i_trial]:
                self.trials.choice_left[i_trial] = False  # Left not chosen
            else:
                self.trials.choice_left[i_trial] = True
            # Feedback waiting time
            if str(MatrixState.WaitForPunish) in states_visited_this_trial_names:
                wait_for_punish_state_times = states_visited_this_trial_times[
                    str(MatrixState.WaitForPunish)]
                wait_for_punish_start_state_times = states_visited_this_trial_times[
                    str(MatrixState.WaitForPunishStart)]
                self.trials.feedback_time[i_trial] = wait_for_punish_state_times[
                    -1][1] - wait_for_punish_start_state_times[0][0]
            else:  # It was a  RegisterWrongWaitCorrect state
                self.trials.feedback_time[i_trial] = None
        # CorrectChoice
        elif str(MatrixState.WaitForRewardStart) in \
                states_visited_this_trial_names:
            self.trials.choice_correct[i_trial] = True
            if self.trials.catch_trial[i_trial]:
                catch_stim_idx = get_catch_stim_idx(
                    self.trials.stimulus_omega[i_trial])
                # Lookup the stimulus probability and increase by its
                # 1/frequency.
                stim_val = self.trials.stimulus_omega[i_trial] * 100
                if stim_val < 50:
                    stim_val = 100 - stim_val
                stim_prob = self.task_parameters.OmegaTable.columns.OmegaProb[
                    self.task_parameters.OmegaTable.columns.Omega.index(
                        stim_val)]
                sum_all_prob = sum(
                    self.task_parameters.OmegaTable.columns.OmegaProb)
                stim_prob = (1 + sum_all_prob - stim_prob) / sum_all_prob
                self.trials.catch_count[catch_stim_idx] += stim_prob
                self.trials.last_success_catch_trial = i_trial
            # Feedback waiting time
            if str(MatrixState.WaitForReward) in states_visited_this_trial_names:
                wait_for_reward_state_times = states_visited_this_trial_times[
                    str(MatrixState.WaitForReward)]
                wait_for_reward_start_state_times = states_visited_this_trial_times[
                    str(MatrixState.WaitForRewardStart)]
                self.trials.feedback_time[i_trial] = wait_for_reward_state_times[
                    -1][1] - wait_for_reward_start_state_times[0][0]
                # Correct choice = left
                if self.trials.left_rewarded[i_trial]:
                    self.trials.choice_left[i_trial] = True  # Left chosen
                else:
                    self.trials.choice_left[i_trial] = False
            else:
                warning("'WaitForReward' state should always appear"
                        " if 'WaitForRewardStart' was initiated")
        elif str(MatrixState.broke_fixation) in states_visited_this_trial_names:
            self.trials.fix_broke[i_trial] = True
        elif str(MatrixState.early_withdrawal) in states_visited_this_trial_names:
            self.trials.early_withdrawal[i_trial] = True
        elif str(MatrixState.timeOut_missed_choice) in \
                states_visited_this_trial_names:
            self.trials.feedback[i_trial] = False
            self.trials.missed_choice[i_trial] = True
        if str(MatrixState.timeOut_SkippedFeedback) in \
                states_visited_this_trial_names:
            self.trials.feedback[i_trial] = False
        if str(MatrixState.Reward) in states_visited_this_trial_names:
            self.trials.rewarded[i_trial] = True
            self.trials.reward_received_total[i_trial] += \
                self.task_parameters.RewardAmount
        if str(MatrixState.CenterPortRewardDelivery) in \
                states_visited_this_trial_names and \
           self.task_parameters.RewardAfterMinSampling:
            self.trials.reward_after_min_sampling[i_trial] = True
            self.trials.reward_received_total[i_trial] += \
                self.task_parameters.CenterPortRewAmount
        if str(MatrixState.WaitCenterPortOut) in states_visited_this_trial_names:
            wait_center_port_out_state_times = states_visited_this_trial_times[
                str(MatrixState.WaitCenterPortOut)]
            self.trials.reaction_time[i_trial] = diff(
                wait_center_port_out_state_times)
        else:
            # Assign with -1 so we can differentiate it from None trials
            # where the state potentially existed but we didn't calculate it
            self.trials.reaction_time[i_trial] = -1
        # State-independent fields
        self.trials.stim_delay[i_trial] = self.task_parameters.StimDelay
        self.trials.feedback_delay[i_trial] = self.task_parameters.FeedbackDelay
        self.trials.min_sample[i_trial] = self.task_parameters.MinSample
        self.trials.reward_magnitude[i_trial + 1] = [
            self.task_parameters.RewardAmount,
            self.task_parameters.RewardAmount]
        self.trials.center_port_rew_amount[
            i_trial + 1] = self.task_parameters.CenterPortRewAmount
        self.trials.pre_stim_cntr_reward[
            i_trial + 1] = self.task_parameters.PreStimDelayCntrReward
        self.timer.custom_extract_data[i_trial] = time.time()

        # IF we are running grating experiments,
        # add the grating orientation that was used
        if self.task_parameters.ExperimentType == \
                ExperimentType.GratingOrientation:
            self.trials.grating_orientation[
                i_trial] = self.draw_params.grating_orientation

        # Updating Delays
        # stimulus delay
        if self.task_parameters.StimDelayAutoincrement:
            if self.trials.fix_broke[i_trial]:
                self.task_parameters.StimDelay = max(
                    self.task_parameters.StimDelayMin,
                    min(self.task_parameters.StimDelayMax,
                        self.trials.stim_delay[
                            i_trial] - self.task_parameters.StimDelayDecr))
            else:
                self.task_parameters.StimDelay = min(
                    self.task_parameters.StimDelayMax,
                    max(self.task_parameters.StimDelayMin,
                        self.trials.stim_delay[
                            i_trial] + self.task_parameters.StimDelayIncr))
        else:
            if not self.trials.fix_broke[i_trial]:
                self.task_parameters.StimDelay = random_unif(
                    self.task_parameters.StimDelayMin,
                    self.task_parameters.StimDelayMax)
            else:
                self.task_parameters.StimDelay = self.trials.stim_delay[i_trial]
        self.timer.custom_stim_delay[i_trial] = time.time()

        # min sampling time
        if self.task_parameters.MinSampleType == MinSampleType.FixMin:
            self.task_parameters.MinSample = \
                self.task_parameters.MinSampleMin
        elif self.task_parameters.MinSampleType == \
                MinSampleType.AutoIncr:
            # Check if animal completed pre-stimulus delay successfully
            if not (self.trials.fix_broke[i_trial] and i_trial >
                    self.task_parameters.StartEasyTrials):
                if self.trials.rewarded[i_trial]:
                    min_sample_incremented = self.trials.min_sample[
                        i_trial] + self.task_parameters.MinSampleIncr
                    self.task_parameters.MinSample = min(
                        self.task_parameters.MinSampleMax,
                        max(self.task_parameters.MinSampleMin,
                            min_sample_incremented))
                elif self.trials.early_withdrawal[i_trial]:
                    min_sample_decremented = self.trials.min_sample[
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
                        self.trials.min_sample[i_trial]))
        elif self.task_parameters.MinSampleType == \
                MinSampleType.RandBetMinMax_DefIsMax:
            use_rand = rand(
                1, 1) < self.task_parameters.MinSampleRandProb
            if not use_rand or i_trial <= self.task_parameters.StartEasyTrials:
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
            if not use_rand or i_trial <= self.task_parameters.StartEasyTrials:
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
                    intervals = list(arange(
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
        self.timer.custom_min_sampling[i_trial] = time.time()

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
            if not self.trials.feedback[i_trial]:
                feedback_delay_decremented = self.trials.feedback_delay[
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
                feedback_delay_incremented = self.trials.feedback_delay[
                    i_trial] + self.task_parameters.FeedbackDelayIncr
                self.task_parameters.FeedbackDelay = min(
                    self.task_parameters.FeedbackDelayMax,
                    max(self.task_parameters.FeedbackDelayMin,
                        feedback_delay_incremented))
        elif FeedbackDelaySelection.TruncExp:
            self.task_parameters.FeedbackDelay = truncated_exponential(
                self.task_parameters.FeedbackDelayMin,
                self.task_parameters.FeedbackDelayMax,
                self.task_parameters.FeedbackDelayTau)
        elif FeedbackDelaySelection.Fix:
            #     ATTEMPT TO GRAY OUT FIELDS
            if self.task_parametersMeta.feedback_delay.Style != 'edit':
                self.task_parametersMeta.feedback_delay.Style = 'edit'
            self.task_parameters.FeedbackDelay = \
                self.task_parameters.FeedbackDelayMax
        else:
            error('Unexpected FeedbackDelaySelection value')
        self.timer.custom_feedback_delay[i_trial] = time.time()

        # Drawing future trials

        # Calculate bias
        # Consider bias only on the last 8 trials/
        # indicesRwdLi = find(self.trials.rewarded,8,'last');
        # if length(indicesRwdLi) ~= 0
        #   indicesRwd = indicesRwdLi(1);
        # else
        #   indicesRwd = 1;
        # end
        LAST_TRIALS = 10
        indicesRwd = iff(i_trial > LAST_TRIALS, i_trial - LAST_TRIALS, 0)
        # ndxRewd = self.trials.rewarded(indicesRwd:i_trial);
        choice_correct_slice = self.trials.choice_correct[
            indicesRwd: i_trial + 1]
        choice_left_slice = self.trials.choice_left[indicesRwd: i_trial + 1]
        left_rewarded_slice = self.trials.left_rewarded[indicesRwd: i_trial + 1]
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
            denominator = iff(sum(filter(None,ndxRightRewDone)),sum(filter(None,ndxRightRewDone)) * 2, 1)
            PerfL = 1 - (sum(filter(None,ndxRightRewd)) / (denominator * 2))
        else:
            PerfL = sum(filter(None,ndxLeftRewd)) / sum(filter(None,ndxLeftRewDone))
        if not any(ndxRightRewDone):
            denominator = iff(sum(filter(None,ndxLeftRewDone)),sum(filter(None,ndxLeftRewDone)) * 2, 1)
            PerfR = 1 - (sum(filter(None,ndxLeftRewd)) / (denominator* 2))
        else:
            PerfR = sum(filter(None,ndxRightRewd)) / sum(filter(None,ndxRightRewDone))
        self.task_parameters.CalcLeftBias = (PerfL - PerfR) / 2 + 0.5

        choice_made_trials = [
            choice_c is not None for choice_c in self.trials.choice_correct]
        rewarded_trials_count = sum(r is True for r in self.trials.rewarded)
        length_choice_made_trials = sum(x for x in choice_made_trials if True)
        if length_choice_made_trials >= 1:
            performance = rewarded_trials_count / length_choice_made_trials
            self.task_parameters.Performance = [
                f'{performance * 100:.2f}', '#/',
                str(length_choice_made_trials), 'T']
            performance = rewarded_trials_count / (i_trial + 1)
            self.task_parameters.AllPerformance = [
                f'{performance * 100:.2f}', '#/', str(i_trial + 1), 'T']
            NUM_LAST_TRIALS = 20
            if i_trial > NUM_LAST_TRIALS:
                if length_choice_made_trials > NUM_LAST_TRIALS:
                    rewarded_trials_ = choice_made_trials[
                        length_choice_made_trials - NUM_LAST_TRIALS + 1:
                        length_choice_made_trials + 1]
                    performance = sum(rewarded_trials_) / NUM_LAST_TRIALS
                    self.task_parameters.Performance = [
                        self.task_parameters.Performance, ' - ',
                        f'{performance * 100:.2f}', '#/',
                        str(NUM_LAST_TRIALS), 'T']
                rewarded_trials_count = sum(self.trials.rewarded[
                    i_trial - NUM_LAST_TRIALS + 1: i_trial + 1])
                performance = rewarded_trials_count / NUM_LAST_TRIALS
                self.task_parameters.AllPerformance = [
                    self.task_parameters.AllPerformance, ' - ',
                    f'{performance * 100:.2f}', '#/', str(NUM_LAST_TRIALS),
                    'T']
        self.timer.custom_calc_bias[i_trial] = time.time()

        # Create future trials
        # Check if its time to generate more future trials
        if i_trial+1 >= self.DVs_already_generated:
            # Do bias correction only if we have enough trials
            # sum(ndxRewd) > Const.BIAS_CORRECT_MIN_RWD_TRIALS
            if self.task_parameters.CorrectBias and i_trial+1 > 7:
                left_bias = self.task_parameters.CalcLeftBias
                # if left_bias < 0.2 || left_bias > 0.8 # Bias is too much,
                # swing it all the way to the other side
                # left_bias = round(left_bias);
                # else
                if 0.45 <= left_bias <= 0.55:
                    left_bias = 0.5
                if left_bias is None:
                    print('Left bias is None.')
                    left_bias = 0.5
            else:
                left_bias = self.task_parameters.LeftBias
            self.timer.custom_adjust_bias[i_trial] = time.time()

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
            self.timer.custom_calc_omega[i_trial] = time.time()
            self.assign_future_trials(i_trial+1,Const.PRE_GENERATE_TRIAL_COUNT)

            self.timer.custom_gen_new_trials[i_trial] = time.time()
        else:
            self.timer.custom_adjust_bias[i_trial] = 0
            self.timer.custom_calc_omega[i_trial] = 0
            self.timer.custom_prep_new_trials[i_trial] = 0
            self.timer.custom_gen_new_trials[i_trial] = 0

        if self.task_parameters.ExperimentType == \
                    ExperimentType.Auditory:
            DV = calc_aud_click_train(self,i_trial+1)
        elif self.task_parameters.ExperimentType == \
                ExperimentType.LightIntensity:
            DV = calc_light_intensity(self, i_trial+1)
        elif self.task_parameters.ExperimentType == \
                ExperimentType.GratingOrientation:
            DV = calc_grating_orientation(self,i_trial+1)
        elif self.task_parameters.ExperimentType == \
                ExperimentType.RandomDots:
            DV = calc_dots_coherence(self, i_trial+1)
        else:
            error('Unexpected ExperimentType')
        self.trials.DV[i_trial+1] = DV

        # Update RDK GUI
        self.task_parameters.OmegaTable.columns.RDK = [
            (value - 50) * 2
            for value in self.task_parameters.OmegaTable.columns.Omega
        ]
        # Set current stimulus for next trial
        DV = self.trials.DV[i_trial + 1]
        if self.task_parameters.ExperimentType == \
                ExperimentType.RandomDots:
            self.task_parameters.CurrentStim = \
                f"{abs(DV / 0.01)}{iff(DV < 0, '# R cohr.', '# L cohr.')}"
        else:
            # Set between -100 to +100
            stim_intensity = f'{iff(DV > 0, (DV + 1) / 0.02, (DV - 1) / -0.02)}'
            self.task_parameters.CurrentStim = \
                f"{stim_intensity}{iff(DV < 0, '# R', '# L')}"

        self.timer.custom_finalize_update[i_trial] = time.time()

        # determine if optogentics trial
        opto_enabled = rand(1, 1) < self.task_parameters.OptoProb
        if i_trial < self.task_parameters.StartEasyTrials:
            opto_enabled = False
        self.trials.opto_enabled[i_trial + 1] = opto_enabled
        self.task_parameters.IsOptoTrial = iff(
            opto_enabled, 'true', 'false')

        # determine if catch trial
        if i_trial < self.task_parameters.StartEasyTrials or \
                self.task_parameters.PercentCatch == 0:
            self.trials.catch_trial[i_trial + 1] = False
        else:
            every_n_trials = round(1 / self.task_parameters.PercentCatch)
            limit = round(every_n_trials * 0.2)
            lower_limit = every_n_trials - limit
            upper_limit = every_n_trials + limit
            if not self.trials.rewarded[i_trial] or i_trial + 1 < \
                    self.trials.last_success_catch_trial + lower_limit:
                self.trials.catch_trial[i_trial + 1] = False
            elif i_trial + 1 < self.trials.last_success_catch_trial + upper_limit:
                # TODO: If OmegaProb changed since last time, then redo it
                non_zero_prob = [
                    self.task_parameters.OmegaTable.Omega[i] / 100
                    for i, prob in enumerate(
                        self.task_parameters.OmegaTable.columns.OmegaProb)
                    if prob > 0]
                complement_non_zero_prob = [1 - prob for prob in non_zero_prob]
                inverse_non_zero_prob = non_zero_prob[::-1]
                active_stim_idxs = get_catch_stim_idx(
                    complement_non_zero_prob + inverse_non_zero_prob)
                cur_stim_idx = get_catch_stim_idx(
                    self.trials.stimulus_omega[i_trial + 1])
                min_catch_counts = min(
                    self.trials.catch_count[i] for i in active_stim_idxs)
                min_catch_idxs = list(set(active_stim_idxs).intersection(
                    {i for i, cc in enumerate(
                        self.trials.catch_count)
                     if floor(cc) == min_catch_counts}))
                self.trials.catch_trial[
                    i_trial + 1] = cur_stim_idx in min_catch_idxs
            else:
                self.trials.catch_trial[i_trial + 1] = True
        # Create as char vector rather than string so that
        # GUI sync doesn't complain
        self.task_parameters.IsCatch = iff(
            self.trials.catch_trial[i_trial + 1], 'true', 'false')
        # Determine if Forced LED trial:
        if self.task_parameters.PortLEDtoCueReward:
            self.trials.forced_led_trial[i_trial + 1] = rand(1, 1) < \
                self.task_parameters.PercentForcedLEDTrial
        else:
            self.trials.forced_led_trial[i_trial + 1] = False
        self.timer.custom_catch_n_force_led[i_trial] = time.time()


class TimerData:
    def __init__(self):
        self.start_new_iter = datalist()
        self.sync_gui = datalist()
        self.build_state_matrix = datalist()
        self.send_state_matrix = datalist()
        self.append_data = datalist()
        self.handle_pause = datalist()
        self.update_custom_data_fields = datalist()
        self.send_plot_data = datalist()
        self.save_data = datalist()
        self.calcilate_timeout = datalist()
        self.custom_extract_data = datalist()
        self.custom_adjust_bias = datalist()
        self.custom_calc_omega = datalist()
        self.custom_initialize = datalist()
        self.custom_finalize_update = datalist()
        self.custom_catch_n_force_led = datalist()
        self.custom_stim_delay = datalist()
        self.custom_min_sampling = datalist()
        self.custom_feedback_delay = datalist()
        self.custom_calc_bias = datalist()
        self.custom_prep_new_trials = datalist()
        self.custom_gen_new_trials = datalist()


class DrawParams:
    def __init__(self):
        self.stim_type = None
        self.grating_orientation = None
        self.num_cycles = None
        self.cycles_per_second_drift = None
        self.phase = None
        self.gabor_size_factor = None
        self.gaussian_filter_ratio = None
        self.center_x = None
        self.center_y = None
        self.aperture_size_width = None
        self.aperture_size_height = None
        self.draw_ratio = None
        self.main_direction = None
        self.dot_speed = None
        self.dot_lifetime_secs = None
        self.coherence = None
        self.screen_width_cm = None
        self.screen_dist_cm = None
        self.dot_size_in_degs = None

class Trials:

    _DEFAULT_CATCH_COUNT_LEN = 21
    def __init__(self,task_parameters):
        self.task_parameters = task_parameters
        self.choice_left = datalist(None)
        self.choice_correct = datalist(None)
        self.feedback = datalist(None)
        self.feedback_time = datalist(None)
        self.feedback_delay = datalist(None)
        self.fix_broke = datalist(None)
        self.early_withdrawal = datalist(None)
        self.missed_choice = datalist(None)
        self.fix_dur = datalist(None)
        self.mt = datalist(None)
        self.catch_trial = datalist(None)
        self.st = datalist(None)
        self.opto_enabled = datalist(None)
        self.rewarded = datalist(None)
        self.reward_after_min_sampling = datalist(False)
        self.pre_stim_counter_reward = datalist(None)
        self.pre_stim_cntr_reward = datalist(size=NUM_OF_TRIALS + 1)
        self.min_sample = datalist(None)
        self.light_intensity_left = datalist()
        self.light_intensity_right = datalist()
        self.grating_orientation = datalist(None)
        self.reward_magnitude = datalist([
            self.task_parameters.RewardAmount,
            self.task_parameters.RewardAmount
        ])
        self.reward_received_total = datalist(size=NUM_OF_TRIALS + 1)
        self.reaction_time = datalist(None)
        self.center_port_rew_amount = datalist(
            self.task_parameters.CenterPortRewAmount)
        self.trial_number = datalist(None)
        self.forced_led_trial = datalist(None)
        self.catch_count = datalist(size=self._DEFAULT_CATCH_COUNT_LEN)
        self.last_success_catch_trial = True
        self.stimulus_omega = datalist(None)
        self.stim_delay = datalist(None)
        self.left_rewarded = datalist(None)
        self.DV = datalist()
        self.trial_start_sys_time = datalist(None)
        self.dots_coherence = datalist(None)
        self.early_withdrawal_timer_start = None

class Data:
    def __init__(self, session, task_parameters):
        self.task_parameters = task_parameters
        self.raw_data = RawData(session)
        self.timer = TimerData()
        self.custom = CustomData(task_parameters, self.timer, self.raw_data)
        self.trail_start_timestamp = datalist()
        self.trail_start_timestamp = datalist()
        self.settings_file = None
        self.dots_mapped_file = None
