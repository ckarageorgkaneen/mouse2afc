import logging
import math
import numpy as np
import itertools

from pybpodapi.protocol import Bpod
from pybpodapi.protocol import StateMachine
from pybpodapi.state_machine.state_machine_base import SMAError

from  mouse2afc.definitions.constant import Constant as Const
from  mouse2afc.definitions.draw_stim_type import DrawStimType
from  mouse2afc.definitions.experiment import ExperimentType
from  mouse2afc.definitions.incorrect_choice_signal_type import IncorrectChoiceSignalType
from  mouse2afc.definitions.iti_signal_type import ITISignalType
from  mouse2afc.definitions.matrix_state import MatrixState
from  mouse2afc.definitions.visual_stim_angle import VisualStimAngle
from  mouse2afc.definitions.stim_after_poke_out import StimAfterPokeOut

from  mouse2afc.utils import enc_trig
from  mouse2afc.utils import get_valve_times
from  mouse2afc.utils import floor
from  mouse2afc.utils import iff
from  mouse2afc.utils import mod
from  mouse2afc.utils import round

logger = logging.getLogger(__name__)

EMULATOR_MODE = True

PORT_STR = 'Port'
PWM_STR = 'PWM'
OUT_STR = 'Out'
IN_STR = 'In'

DEFAULT_WIRE_TTL_DURATION = 0.02
DEFAULT_LED_ERROR_RATE = 0.1


class PluginSerialPorts:
    pass


class StateMatrixError(SMAError):
    pass


def error(message):
    logger.error(message)
    raise StateMatrixError(message)


def fwrite(port, millis, type):
    pass


def pwm_str(port):
    return f'{PWM_STR}{str(port)}'


def port_str(port, out=False):
    return f'{PORT_STR}{str(port)}{OUT_STR if out else IN_STR}'

def single_experiment_stimulus(self,task_parameters,data,i_trial,experiment_level):
    "Assigns stimuli according to experiment type"
    if experiment_level == ExperimentType.auditory:
        # In MATLAB: 'BNCState' instead of 'BNC1'
        _deliver_stimulus = [('BNC1', 1)]
        _cont_deliver_stimulus = []
        _stop_stimulus = [('BNC1', 0)]
    elif experiment_level == \
            ExperimentType.light_intensity:
        # Divide Intensity by 100 to get fraction value
        left_pwm_stim = round(
            data.custom.trials.light_intensity_left[i_trial] * self.left_pwm / 100)
        right_pwm_stim = round(
            data.custom.trials.light_intensity_right[
                i_trial] * self.right_pwm / 100)
        _deliver_stimulus = [
            (pwm_str(self.left_port), left_pwm_stim),
            (pwm_str(self.right_port), right_pwm_stim)
        ]
        _cont_deliver_stimulus = _deliver_stimulus
        _stop_stimulus =  []
    elif experiment_level == \
            ExperimentType.grating_orientation:
        right_port_angle = VisualStimAngle.get_degrees(
            task_parameters.visual_stim_angle_port_right.value)
        left_port_angle = VisualStimAngle.get_degrees(
            task_parameters.visual_stim_angle_port_left.value)
        # Calculate the distance between right and left port angle to
        # determine whether we should use the circle arc between the two
        # values in the clock-wise or counter-clock-wise direction to
        # calculate the different difficulties.
        ccw = iff(mod(right_port_angle - left_port_angle, 360) < mod(
            left_port_angle - right_port_angle, 360), True, False)
        if ccw:
            final_DV = data.custom.trials.DV[i_trial]
            if right_port_angle < left_port_angle:
                right_port_angle += 360
            angle_diff = right_port_angle - left_port_angle
            min_angle = left_port_angle
        else:
            final_DV = -data.custom.trials.DV[i_trial]
            if left_port_angle < right_port_angle:
                left_port_angle += 360
            angle_diff = left_port_angle - right_port_angle
            min_angle = right_port_angle
        # orientation = ((DVMax - DV)*(DVMAX-DVMin)*(
        #   MaxAngle - MinANgle)) + MinAngle
        grating_orientation = ((1 - final_DV) * angle_diff / 2) + min_angle
        grating_orientation = mod(grating_orientation, 360)
        data.custom.draw_params.stim_type = DrawStimType.static_gratings
        data.custom.draw_params.grating_orientation = grating_orientation
        data.custom.draw_params.num_cycles = task_parameters.num_cycles
        data.custom.draw_params.cycles_per_second_drift = \
            task_parameters.cycles_per_second_drift
        data.custom.draw_params.phase = task_parameters.phase
        data.custom.draw_params.gabor_size_factor = \
            task_parameters.gabor_size_factor
        data.custom.draw_params.gaussian_filter_ratio = \
            task_parameters.gaussian_filter_ratio
        # Start from the 5th byte
        # serializeAndWrite(data.dotsMapped_file, 5,
        #                   data.custom.draw_params)
        # data.dotsMapped_file.data(1: 4) = typecast(uint32(1), 'uint8');

        _deliver_stimulus = [('SoftCode', 5)]
        _cont_deliver_stimulus = []
        _stop_stimulus =  [('SoftCode', 6)]
    elif experiment_level == ExperimentType.random_dots:
        # Setup the parameters
        # Use 20% of the screen size. Assume apertureSize is the diameter
        task_parameters.circleArea = math.pi * \
            ((task_parameters.aperture_size_width / 2) ** 2)
        task_parameters.n_dots = round(
            task_parameters.circle_area * task_parameters.draw_ratio)

        data.custom.draw_params.stimType = DrawStimType.rdk
        data.custom.draw_params.center_x = task_parameters.center_x
        data.custom.draw_params.center_y = task_parameters.center_y
        data.custom.draw_params.aperture_size_width = \
            task_parameters.aperture_size_width
        data.custom.draw_params.aperture_size_height = \
            task_parameters.aperture_size_height
        data.custom.draw_params.draw_ratio = task_parameters.draw_ratio
        data.custom.draw_params.main_direction = floor(
            VisualStimAngle.get_degrees(
                iff(self.is_left_rewarded,
                    task_parameters.visual_stim_angle_port_left.value,
                    task_parameters.visual_stim_angle_port_right.value)))
        data.custom.draw_params.dot_speed = \
            task_parameters.dot_speed_degs_per_sec
        data.custom.draw_params.dot_lifetime_secs = \
            task_parameters.dot_lifetime_secs
        data.custom.draw_params.coherence = data.custom.trials.dots_coherence[
            i_trial]
        data.custom.draw_params.screen_width_cm = \
            task_parameters.screen_width_cm
        data.custom.draw_params.screen_dist_cm = \
            task_parameters.screen_dist_cm
        data.custom.draw_params.dot_size_in_degs = \
            task_parameters.dot_size_in_degs

        # Start from the 5th byte
        # serializeAndWrite(data.dotsMapped_file, 5,
        #                   data.custom.draw_params)
        # data.dotsMapped_file.data(1: 4) = \
        #   typecast(uint32(1), 'uint8');

        _deliver_stimulus = [('SoftCode', 5)]
        _cont_deliver_stimulus = []
        _stop_stimulus = [('SoftCode', 6)]
    elif experiment_level == ExperimentType.no_stimulus:
        _deliver_stimulus = []
        _cont_deliver_stimulus = []
        _stop_stimulus = []
    else:
        error('Unexpected Experiment Type')

    return _deliver_stimulus,_cont_deliver_stimulus,_stop_stimulus

def handle_state_matrix_stim(self,task_parameters,data,i_trial):
    "combines the stimuli of the primary and secondary experiments"
    primary_stimulus = single_experiment_stimulus(
        self,task_parameters,data,i_trial,
        task_parameters.primary_experiment_type)
    secondary_stimulus = single_experiment_stimulus(
        self,task_parameters,data,i_trial,
        task_parameters.secondary_experiment_type)

    deliver_stimulus = [primary_stimulus[0],secondary_stimulus[0]]
    cont_deliver_stimulus = [primary_stimulus[1],secondary_stimulus[1]]
    stop_stimulus = [primary_stimulus[2],secondary_stimulus[2]]

    return deliver_stimulus,cont_deliver_stimulus,stop_stimulus

class StateMatrix(StateMachine):
    def __init__(self, bpod, task_parameters, data, i_trial):
        super().__init__(bpod)
        # Define ports
        left_port = floor(mod(task_parameters.ports_lmr_air / 100000, 10))
        center_port = floor(mod(task_parameters.ports_lmr_air / 10000, 10))
        right_port = floor(mod(task_parameters.ports_lmr_air / 1000, 10))
        left_port_out = port_str(left_port, out=True)
        center_port_out = port_str(center_port, out=True)
        right_port_out = port_str(right_port, out=True)
        left_port_in = port_str(left_port)
        center_port_in = port_str(center_port)
        right_port_in = port_str(right_port)

        # Duration of the TTL signal to denote start and end of trial for 2P
        wire_ttl_duration = DEFAULT_WIRE_TTL_DURATION

        # PWM = (255 * (100-Attenuation))/100
        left_pwm = round((100 - task_parameters.left_poke_atten_prcnt) * 2.55)
        center_pwm = round(
            (100 - task_parameters.center_poke_atten_prcnt) * 2.55)
        right_pwm = round(
            (100 - task_parameters.right_poke_atten_prcnt) * 2.55)

        led_error_rate = DEFAULT_LED_ERROR_RATE

        is_left_rewarded = data.custom.trials.left_rewarded[i_trial]

        #created to be used by `handle_state_matrix_stim`
        self.left_port = left_port
        self.center_port = center_port
        self.right_port = right_port
        self.left_pwm = left_pwm
        self.center_pwm = center_pwm
        self.right_pwm = right_pwm
        self.is_left_rewarded = is_left_rewarded

        stimuli = handle_state_matrix_stim(self,task_parameters,data,i_trial)
        deliver_stimulus = list(itertools.chain.from_iterable(stimuli[0]))
        cont_deliver_stimulus = list(itertools.chain.from_iterable(stimuli[1]))
        stop_stimulus = list(itertools.chain.from_iterable(stimuli[2]))

        if task_parameters.stim_after_poke_out == StimAfterPokeOut.not_used:
            wait_for_decision_stim = stop_stimulus
            wait_feedback_stim = stop_stimulus
            wait_for_poke_out_stim = stop_stimulus
        elif task_parameters.stim_after_poke_out == StimAfterPokeOut.until_feedback_start:
            wait_for_decision_stim = cont_deliver_stimulus
            wait_feedback_stim = stop_stimulus
            wait_for_poke_out_stim = stop_stimulus
        elif task_parameters.stim_after_poke_out == StimAfterPokeOut.until_feedback_end:
            wait_for_decision_stim = cont_deliver_stimulus
            wait_feedback_stim = cont_deliver_stimulus
            wait_for_poke_out_stim = stop_stimulus
        elif task_parameters.stim_after_poke_out == StimAfterPokeOut.until_end_of_trial:
            wait_for_decision_stim = cont_deliver_stimulus
            wait_feedback_stim = cont_deliver_stimulus
            wait_for_poke_out_stim = cont_deliver_stimulus
        else:
            error('Unexpected Stim After Poke Out Option')

        # Valve opening is a bitmap. Open each valve separately by raising 2 to
        # the power of port number - 1
        # left_valve = 2 ** (left_port - 1)
        # center_valve = 2 ** (center_port - 1)
        # right_valve = 2 ** (right_port - 1)
        left_valve = left_port
        center_valve = center_port
        right_valve = right_port

        right_valve_time = get_valve_times(
            data.custom.trials.reward_magnitude[i_trial][0], left_port)
        center_valve_time = get_valve_times(
            data.custom.trials.center_port_rew_amount[i_trial], center_port)
        right_valve_time = get_valve_times(
            data.custom.trials.reward_magnitude[i_trial][1], right_port)

        incorrect_consequence = iff(
            not task_parameters.habituate_ignore_incorrect,
            str(MatrixState.WaitForPunishStart),
            str(MatrixState.RegisterWrongWaitCorrect))
        left_action_state = iff(is_left_rewarded, str(
            MatrixState.WaitForRewardStart), incorrect_consequence)
        right_action_state = iff(is_left_rewarded, incorrect_consequence, str(
            MatrixState.WaitForRewardStart))
        reward_in = iff(is_left_rewarded, left_port_in, right_port_in)
        reward_out = iff(is_left_rewarded, left_port_out, right_port_out)
        punish_in = iff(is_left_rewarded, right_port_in, left_port_in)
        punish_out = iff(is_left_rewarded, right_port_out, left_port_out)
        valve_time = iff(is_left_rewarded, right_valve_time, right_valve_time)
        valve_code = iff(is_left_rewarded, left_valve, right_valve)

        # Check if to play beep at end of minimum sampling
        min_sample_beep = iff(task_parameters.beep_after_min_sampling, [
                            ('SoftCode', 12)], [])
        min_sample_beep_duration = iff(
            task_parameters.beep_after_min_sampling, 0.01, 0)
        # GUI option Reward After Min Sampling
        # If center - reward is enabled, then a reward is given once min_sample
        # is over and no further sampling is given.
        reward_center_port = iff(task_parameters.reward_after_min_sampling,
                               [('Valve', center_valve)] + stop_stimulus,
                               cont_deliver_stimulus)
        timer_cprd = iff(
            task_parameters.reward_after_min_sampling, center_valve_time,
            task_parameters.stimulus_time - task_parameters.min_sample)

        # White Noise played as Error Feedback
        error_feedback = iff(task_parameters.play_noise_for_error, [(
            'SoftCode', 11)], [])

        # CatchTrial
        feedback_delay_correct = iff(data.custom.trials.catch_trial[
            i_trial], Const.FEEDBACK_CATCH_MAX_SEC,
            max(task_parameters.feedback_delay,0.01))

        # GUI option CatchError
        feedback_delay_punish = iff(task_parameters.catch_error,
                                  Const.FEEDBACK_CATCH_MAX_SEC,
                                  max(task_parameters.feedback_delay,0.01))
        skipped_feeback_signal = iff(
            task_parameters.catch_error, [], error_feedback)

        #Incorrect Timeout
        incorrect_timeout = iff(not task_parameters.pc_timeout,
                               task_parameters.timeout_incorrect_choice
                               + task_parameters.iti,
                               .01)

        # Incorrect Choice signal
        if task_parameters.incorrect_choice_signal_type == \
                IncorrectChoiceSignalType.noise_pulse_pal:
            punishment_duration = 0.01
            incorrect_choice_signal = [('SoftCode', 11)]
        elif task_parameters.incorrect_choice_signal_type == \
                IncorrectChoiceSignalType.beep_on_wire1:
            punishment_duration = 0.25
            incorrect_choice_signal = [('Wire1', 1)]
        elif task_parameters.incorrect_choice_signal_type == \
                IncorrectChoiceSignalType.port_led:
            punishment_duration = 0.1
            incorrect_choice_signal = [
                (pwm_str(left_port), left_pwm),
                (pwm_str(center_port), center_pwm),
                (pwm_str(right_port), right_pwm)
            ]
        elif task_parameters.incorrect_choice_signal_type == \
                IncorrectChoiceSignalType.none:
            punishment_duration = 0.01
            incorrect_choice_signal = []
        else:
            error('Unexpected Incorrect Choice Signal Type value')

        # ITI signal
        if task_parameters.iti_signal_type == ITISignalType.beep:
            iti_signal_duration = 0.01
            iti_signal = [('SoftCode', 12)]
        elif task_parameters.iti_signal_type == ITISignalType.port_led:
            iti_signal_duration = 0.1
            iti_signal = [
                (pwm_str(left_port), left_pwm),
                (pwm_str(center_port), center_pwm),
                (pwm_str(right_port), right_pwm)
            ]
        elif task_parameters.iti_signal_type == ITISignalType.none:
            iti_signal_duration = 0.01
            iti_signal = []
        else:
            error('Unexpected ITI Signal Type value')

        # Wire1 settings
        wire1_out_error = iff(task_parameters.wire1_video_trigger, [(
                            'Wire2', 2)], [])
        wire1_out_correct_condition = task_parameters.wire1_video_trigger and \
            data.custom.trials.catch_trial[i_trial]
        wire1_out_correct = iff(wire1_out_correct_condition,
                              [('Wire2', 2)], [])

        # LED on the side lateral port to cue the rewarded side at the
        # beginning of the training. On auditory discrimination task, both
        # lateral ports are illuminated after end of stimulus delivery.
        if data.custom.trials.forced_led_trial[i_trial]:
            rewarded_port = iff(is_left_rewarded, left_port, right_port)
            rewarded_port_pwm = iff(is_left_rewarded, left_pwm, right_pwm)
            forced_led_stim = [(pwm_str(rewarded_port), rewarded_port_pwm)]
        elif task_parameters.primary_experiment_type == ExperimentType.auditory:
            forced_led_stim = [
                (pwm_str(left_port), left_pwm),
                (pwm_str(right_port), right_pwm)
            ]
        else:
            forced_led_stim = []

        pc_timeout = task_parameters.pc_timeout
        # Build state matrix
        self.set_global_timer(1, task_parameters.choice_deadline)
        self.set_global_timer(2, feedback_delay_correct)
        self.set_global_timer(3, feedback_delay_punish)
        self.set_global_timer(4, incorrect_timeout)
        self.add_state(state_name=str(MatrixState.ITI_Signal),
                       state_timer=iti_signal_duration,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitForCenterPoke)},
                       output_actions=iti_signal)
        self.add_state(state_name=str(MatrixState.WaitForCenterPoke),
                       state_timer=0,
                       state_change_conditions={
                           center_port_in: str(MatrixState.PreStimReward)},
                       output_actions=[(pwm_str(center_port), center_pwm)])
        self.add_state(state_name=str(MatrixState.PreStimReward),
                       state_timer=iff(task_parameters.pre_stim_delay_cntr_reward,
                                       get_valve_times(task_parameters.pre_stim_delay_cntr_reward,
                                       center_port), 0.01),
                       state_change_conditions={
                           Bpod.Events.Tup:str(MatrixState.TriggerWaitForStimulus)},
                       output_actions=iff(task_parameters.pre_stim_delay_cntr_reward,
                                          [('Valve', center_valve)], []))
        # The next method is useful to close the 2 - photon shutter. It is
        # enabled by setting Optogenetics StartState to this state and end
        # state to ITI.
        self.add_state(state_name=str(MatrixState.TriggerWaitForStimulus),
                       state_timer=wire_ttl_duration,
                       state_change_conditions={
                           center_port_out: str(MatrixState.StimDelayGrace),
                           Bpod.Events.Tup: str(MatrixState.WaitForStimulus)},
                       output_actions=[])
        self.add_state(state_name=str(MatrixState.WaitForStimulus),
                       state_timer=max(0,
                                       task_parameters.stim_delay
                                       - wire_ttl_duration),
                       state_change_conditions={
                           center_port_out: str(MatrixState.StimDelayGrace),
                           Bpod.Events.Tup: str(MatrixState.StimulusDelivery)},
                        output_actions= [])
        self.add_state(state_name=str(MatrixState.StimDelayGrace),
                       state_timer=task_parameters.stim_delay_grace,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.BrokeFixation),
                           center_port_in: str(MatrixState.TriggerWaitForStimulus)},
                       output_actions= [])
        self.add_state(state_name=str(MatrixState.BrokeFixation),
                       state_timer=iff(not pc_timeout,
                                       task_parameters.timeout_broke_fixation,
                                       0.01),
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.ITI)},
                       output_actions=error_feedback)
        self.add_state(state_name=str(MatrixState.StimulusDelivery),
                       state_timer=task_parameters.min_sample
                                    - min_sample_beep_duration
                                    - timer_cprd,
                       state_change_conditions={
                           center_port_out: str(MatrixState.EarlyWithdrawal),
                           Bpod.Events.Tup: str(MatrixState.BeepMinSampling)},
                       output_actions=deliver_stimulus)
        self.add_state(state_name=str(MatrixState.EarlyWithdrawal),
                       state_timer=0,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.TimeoutEarlyWithdrawal)},
                       output_actions=(stop_stimulus + [('SoftCode', 1)]))
        self.add_state(state_name=str(MatrixState.BeepMinSampling),
                       state_timer=min_sample_beep_duration,
                       state_change_conditions={
                           center_port_out: str(MatrixState.TriggerWaitChoiceTimer),
                           Bpod.Events.Tup: str(MatrixState.CenterPortRewardDelivery)},
                       output_actions=(cont_deliver_stimulus + min_sample_beep))
        self.add_state(state_name=str(MatrixState.CenterPortRewardDelivery),
                       state_timer=timer_cprd,
                       state_change_conditions={
                           center_port_out: str(MatrixState.TriggerWaitChoiceTimer),
                           Bpod.Events.Tup: str(MatrixState.StimulusTime)},
                       output_actions=(cont_deliver_stimulus + reward_center_port))
        self.add_state(state_name=str(MatrixState.StimulusTime),
                       state_timer= max(0,task_parameters.stimulus_time
                                        - task_parameters.min_sample
                                        - timer_cprd
                                        - min_sample_beep_duration),
                       state_change_conditions={
                           center_port_out: str(MatrixState.TriggerWaitChoiceTimer),
                           Bpod.Events.Tup: str(MatrixState.WaitCenterPortOut)},
                       output_actions=cont_deliver_stimulus)
        self.add_state(state_name=str(MatrixState.TriggerWaitChoiceTimer),
                       state_timer=0,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitForChoice)},
                       output_actions=(wait_for_decision_stim + forced_led_stim
                                       + [('GlobalTimerTrig', enc_trig(1))]))
        self.add_state(state_name=str(MatrixState.WaitCenterPortOut),
                       state_timer=0,
                       state_change_conditions={
                           center_port_out: str(MatrixState.WaitForChoice),
                           left_port_in: left_action_state,
                           right_port_in: right_action_state,
                           'GlobalTimer1_End': str(MatrixState.TimeoutMissedChoice
                                    )},
                       output_actions=(wait_for_decision_stim + forced_led_stim
                                       + [('GlobalTimerTrig', enc_trig(1))]))
        self.add_state(state_name=str(MatrixState.WaitForChoice),
                       state_timer=0,
                       state_change_conditions={
                           left_port_in: left_action_state,
                           right_port_in: right_action_state,
                           'GlobalTimer1_End': str(MatrixState.TimeoutMissedChoice)},
                       output_actions=(wait_for_decision_stim + forced_led_stim))
        self.add_state(state_name=str(MatrixState.WaitForRewardStart),
                       state_timer=0,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitForReward)},
                       output_actions=(wire1_out_correct + wait_feedback_stim
                                       + [('GlobalTimerTrig', enc_trig(2))]))
        self.add_state(state_name=str(MatrixState.WaitForReward),
                       state_timer=0,
                       state_change_conditions={
                           'GlobalTimer2_End': str(MatrixState.Reward),
                           reward_out: str(MatrixState.RewardGrace)},
                           output_actions=wait_feedback_stim)
        self.add_state(state_name=str(MatrixState.RewardGrace),
                       state_timer=task_parameters.feedback_delay_grace,
                       state_change_conditions={
                           reward_in: str(MatrixState.WaitForReward),
                           Bpod.Events.Tup: str(MatrixState.TimeoutSkippedFeedback),
                           'GlobalTimer2_End': str(MatrixState.TimeoutSkippedFeedback),
                           center_port_in: str(MatrixState.TimeoutSkippedFeedback),
                           punish_in: str(MatrixState.TimeoutSkippedFeedback)},
                       output_actions=wait_feedback_stim)
        self.add_state(state_name=str(MatrixState.Reward),
                       state_timer=valve_time,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitRewardOut)},
                       output_actions=(wait_feedback_stim + [('Valve', valve_code)]))
        self.add_state(state_name=str(MatrixState.WaitRewardOut),
                       state_timer=1,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.ext_ITI),
                           reward_out: str(MatrixState.ext_ITI)},
                       output_actions= ([('GlobalTimerTrig', enc_trig(5))]
                                        + wait_for_poke_out_stim) )
        self.add_state(state_name=str(MatrixState.RegisterWrongWaitCorrect),
                       state_timer=0,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitForChoice)},
                       output_actions=wait_feedback_stim)
        self.add_state(state_name=str(MatrixState.WaitForPunishStart),
                       state_timer=0,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitForPunish)},
                       output_actions=(wire1_out_error + wait_feedback_stim
                                       + [('GlobalTimerTrig', enc_trig(3))]))
        self.add_state(state_name=str(MatrixState.WaitForPunish),
                       state_timer=0,
                       state_change_conditions={
                           'GlobalTimer3_End': str(MatrixState.Punishment),
                           punish_out: str(MatrixState.PunishGrace)},
                       output_actions=wait_feedback_stim)
        self.add_state(state_name=str(MatrixState.PunishGrace),
                       state_timer=task_parameters.feedback_delay_grace,
                       state_change_conditions={
                           punish_in: str(MatrixState.WaitForPunish),
                           Bpod.Events.Tup: str(MatrixState.TimeoutSkippedFeedback),
                           'GlobalTimer3_End': str(MatrixState.TimeoutSkippedFeedback),
                           center_port_in: str(MatrixState.TimeoutSkippedFeedback),
                           reward_in: str(MatrixState.TimeoutSkippedFeedback)},
                       output_actions=wait_feedback_stim)
        self.add_state(state_name=str(MatrixState.Punishment),
                       state_timer=punishment_duration,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitPunishOut),
                           punish_out: str(MatrixState.TimeoutIncorrectChoice)},
                       output_actions=(incorrect_choice_signal + wait_feedback_stim))
        self.add_state(state_name=str(MatrixState.WaitPunishOut),
                       state_timer= 1, #TODO: = task_parameters.waitfinalpokeoutsec
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.TimeoutIncorrectChoice),
                           punish_out: str(MatrixState.TimeoutIncorrectChoice)},
                       output_actions= ([('GlobalTimerTrig', enc_trig(4))] 
                                        + wait_for_poke_out_stim))
        self.add_state(state_name=str(MatrixState.TimeoutEarlyWithdrawal),
                       state_timer=led_error_rate,
                       state_change_conditions={
                           'SoftCode1': str(MatrixState.ITI),
                           Bpod.Events.Tup: str(MatrixState.TimeoutEarlyWithdrawalFlashOn)},
                       output_actions=(stop_stimulus + error_feedback + [('SoftCode',2)]))
        self.add_state(state_name=str(MatrixState.TimeoutEarlyWithdrawalFlashOn),
                       state_timer=led_error_rate,
                       state_change_conditions={
                           'SoftCode1': str(MatrixState.ITI),
                           Bpod.Events.Tup: str(MatrixState.TimeoutEarlyWithdrawal)},
                       output_actions=(stop_stimulus + error_feedback +
                         [(pwm_str(left_port), left_pwm),
                          (pwm_str(right_port), right_pwm)]))
        self.add_state(state_name=str(MatrixState.TimeoutIncorrectChoice),
                       state_timer=0,
                       state_change_conditions={
                           'Condition4': str(MatrixState.ext_ITI)},
                       output_actions= stop_stimulus)
        self.add_state(state_name=str(MatrixState.TimeoutSkippedFeedback),
                       state_timer=iff(not pc_timeout,
                                       task_parameters.timeout_skipped_feedback,
                                       0.01),
                       state_change_conditions={
                          Bpod.Events.Tup: str(MatrixState.ITI)},
                       output_actions=(stop_stimulus + skipped_feeback_signal))
        self.add_state(state_name=str(MatrixState.TimeoutMissedChoice),
                       state_timer=iff(not pc_timeout,
                                       task_parameters.timeout_missed_choice,
                                       0.01),
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.ITI)},
                       output_actions=(stop_stimulus + error_feedback))
        self.add_state(state_name=str(MatrixState.ITI),
                       state_timer=wire_ttl_duration,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.ext_ITI)},
                       output_actions=([('GlobalTimerTrig', enc_trig(5))]+ stop_stimulus))
        self.add_state(state_name=str(MatrixState.ext_ITI),
                       state_timer=iff(not pc_timeout,
                                       task_parameters.iti,
                                       0.01),
                       state_change_conditions={
                           Bpod.Events.Tup: 'exit',
                           'Condition5': 'exit'},
                       output_actions= stop_stimulus)

        # If Optogenetics/2-Photon is enabled for a particular state, then we
        # modify that gien state such that it would send a signal to arduino
        # with the required offset delay to trigger the optogentics box.
        # Note: To precisely track your optogentics signal, split the arduino
        # output to the optogentics box and feed it as an input to Bpod input
        # TTL, e.g Wire1. This way, the optogentics signal gets written as
        # part of your data file. Don't forget to activate that input in the
        # Bpod main config.

        if data.custom.trials.opto_enabled[i_trial]:
            # Convert seconds to millis as we will send ints to Arduino
            opto_delay = np.array(
                [task_parameters.opto_start_delay * 1000], dtype=np.uint32)
            opto_delay = opto_delay.view(np.uint8)
            opto_time = np.array(
                [task_parameters.opto_max_time * 1000], dtype=np.uint32)
            opto_time = opto_time.view(np.uint8)
            if not EMULATOR_MODE or hasattr(PluginSerialPorts, 'OptoSerial'):
                fwrite(PluginSerialPorts.OptoSerial, opto_delay, 'int8')
                fwrite(PluginSerialPorts.OptoSerial, opto_time, 'int8')
            opto_start_event_idx = \
                self.hardware.channels.output_channel_names.index('Wire3')
            opto_stop_event_idx = \
                self.hardware.channels.output_channel_names.index('Wire4')
            tuples = [
                (str(task_parameters.opto_start_state_1), opto_start_event_idx),
                (str(task_parameters.opto_end_state_1), opto_stop_event_idx),
                (str(task_parameters.opto_end_state_2), opto_stop_event_idx),
                (str(MatrixState.ext_ITI), opto_stop_event_idx)
            ]
            for state_name, event_idx in tuples:
                trgt_state_num = self.state_names.index(state_name)
                self.output_matrix[trgt_state_num][event_idx] = 1
