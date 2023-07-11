import logging
import math
import numpy as np

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

from  mouse2afc.utils import EncTrig
from  mouse2afc.utils import GetValveTimes
from  mouse2afc.utils import floor
from  mouse2afc.utils import iff
from  mouse2afc.utils import mod
from  mouse2afc.utils import round

logger = logging.getLogger(__name__)

# TODO: Properly pass emulator mode
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


class StateMatrix(StateMachine):
    def __init__(self, bpod, task_parameters, data, i_trial):
        super().__init__(bpod)
        # Define ports
        left_port = floor(mod(task_parameters.Ports_LMRAir / 100000, 10))
        center_port = floor(mod(task_parameters.Ports_LMRAir / 10000, 10))
        right_port = floor(mod(task_parameters.Ports_LMRAir / 1000, 10))
        left_port_out = port_str(left_port, out=True)
        center_port_out = port_str(center_port, out=True)
        right_port_out = port_str(right_port, out=True)
        left_port_in = port_str(left_port)
        center_port_in = port_str(center_port)
        right_port_in = port_str(right_port)

        # Duration of the TTL signal to denote start and end of trial for 2P
        wire_ttl_duration = DEFAULT_WIRE_TTL_DURATION

        # PWM = (255 * (100-Attenuation))/100
        left_pwm = round((100 - task_parameters.LeftPokeAttenPrcnt) * 2.55)
        center_pwm = round(
            (100 - task_parameters.CenterPokeAttenPrcnt) * 2.55)
        right_pwm = round(
            (100 - task_parameters.RightPokeAttenPrcnt) * 2.55)

        LED_error_rate = DEFAULT_LED_ERROR_RATE

        is_left_rewarded = data.Custom.Trials.LeftRewarded[i_trial]

        if task_parameters.ExperimentType == ExperimentType.Auditory:
            # In MATLAB: 'BNCState' instead of 'BNC1'
            delivery_stimulus = [('BNC1', 1)]
            cont_deliver_stimulus = []
            stop_stimulus = [('BNC1', 0)]
        elif task_parameters.ExperimentType == \
                ExperimentType.LightIntensity:
            # Divide Intensity by 100 to get fraction value
            left_pwm_stim = round(
                data.Custom.Trials.LightIntensityLeft[i_trial] * left_pwm / 100)
            right_pwm_stim = round(
                data.Custom.Trials.LightIntensityRight[
                    i_trial] * right_pwm / 100)
            delivery_stimulus = [
                (pwm_str(left_port), left_pwm_stim),
                (pwm_str(right_port), right_pwm_stim)
            ]
            cont_deliver_stimulus = delivery_stimulus
            stop_stimulus =  []
        elif task_parameters.ExperimentType == \
                ExperimentType.GratingOrientation:
            right_port_angle = VisualStimAngle.get_degrees(
                task_parameters.VisualStimAnglePortRight.value)
            left_port_angle = VisualStimAngle.get_degrees(
                task_parameters.VisualStimAnglePortLeft.value)
            # Calculate the distance between right and left port angle to
            # determine whether we should use the circle arc between the two
            # values in the clock-wise or counter-clock-wise direction to
            # calculate the different difficulties.
            ccw = iff(mod(right_port_angle - left_port_angle, 360) < mod(
                left_port_angle - right_port_angle, 360), True, False)
            if ccw:
                final_DV = data.Custom.Trials.DV[i_trial]
                if right_port_angle < left_port_angle:
                    right_port_angle += 360
                angle_diff = right_port_angle - left_port_angle
                min_angle = left_port_angle
            else:
                final_DV = -data.Custom.Trials.DV[i_trial]
                if left_port_angle < right_port_angle:
                    left_port_angle += 360
                angle_diff = left_port_angle - right_port_angle
                min_angle = right_port_angle
            # orientation = ((DVMax - DV)*(DVMAX-DVMin)*(
            #   MaxAngle - MinANgle)) + MinAngle
            grating_orientation = ((1 - final_DV) * angle_diff / 2) + min_angle
            grating_orientation = mod(grating_orientation, 360)
            data.Custom.drawParams.stimType = DrawStimType.StaticGratings
            data.Custom.drawParams.gratingOrientation = grating_orientation
            data.Custom.drawParams.numCycles = task_parameters.NumCycles
            data.Custom.drawParams.cyclesPerSecondDrift = \
                task_parameters.CyclesPerSecondDrift
            data.Custom.drawParams.phase = task_parameters.Phase
            data.Custom.drawParams.gaborSizeFactor = \
                task_parameters.GaborSizeFactor
            data.Custom.drawParams.gaussianFilterRatio = \
                task_parameters.GaussianFilterRatio
            # Start from the 5th byte
            # serializeAndWrite(data.dotsMapped_file, 5,
            #                   data.Custom.drawParams)
            # data.dotsMapped_file.data(1: 4) = typecast(uint32(1), 'uint8');

            delivery_stimulus = [('SoftCode', 5)]
            cont_deliver_stimulus = []
            stop_stimulus =  [('SoftCode', 6)]
        elif task_parameters.ExperimentType == ExperimentType.RandomDots:
            # Setup the parameters
            # Use 20% of the screen size. Assume apertureSize is the diameter
            task_parameters.circleArea = math.pi * \
                ((task_parameters.ApertureSizeWidth / 2) ** 2)
            task_parameters.nDots = round(
                task_parameters.CircleArea * task_parameters.DrawRatio)

            data.Custom.drawParams.stimType = DrawStimType.RDK
            data.Custom.drawParams.centerX = task_parameters.CenterX
            data.Custom.drawParams.centerY = task_parameters.CenterY
            data.Custom.drawParams.apertureSizeWidth = \
                task_parameters.ApertureSizeWidth
            data.Custom.drawParams.apertureSizeHeight = \
                task_parameters.ApertureSizeHeight
            data.Custom.drawParams.drawRatio = task_parameters.DrawRatio
            data.Custom.drawParams.mainDirection = floor(
                VisualStimAngle.get_degrees(
                    iff(is_left_rewarded,
                        task_parameters.VisualStimAnglePortLeft.value,
                        task_parameters.VisualStimAnglePortRight.value)))
            data.Custom.drawParams.dotSpeed = \
                task_parameters.DotSpeedDegsPerSec
            data.Custom.drawParams.dotLifetimeSecs = \
                task_parameters.DotLifetimeSecs
            data.Custom.drawParams.coherence = data.Custom.Trials.DotsCoherence[
                i_trial]
            data.Custom.drawParams.screenWidthCm = \
                task_parameters.ScreenWidthCm
            data.Custom.drawParams.screenDistCm = \
                task_parameters.ScreenDistCm
            data.Custom.drawParams.dotSizeInDegs = \
                task_parameters.DotSizeInDegs

            # Start from the 5th byte
            # serializeAndWrite(data.dotsMapped_file, 5,
            #                   data.Custom.drawParams)
            # data.dotsMapped_file.data(1: 4) = \
            #   typecast(uint32(1), 'uint8');

            delivery_stimulus = [('SoftCode', 5)]
            cont_deliver_stimulus = []
            stop_stimulus = [('SoftCode', 6)]
        else:
            error('Unexpected ExperimentType')

        if task_parameters.StimAfterPokeOut == StimAfterPokeOut.NotUsed:
            wait_for_decision_stim = stop_stimulus
            wait_feedback_stim = stop_stimulus
            wait_for_poke_out_stim = stop_stimulus
        elif task_parameters.StimAfterPokeOut == StimAfterPokeOut.UntilFeedbackStart:
            wait_for_decision_stim = cont_deliver_stimulus
            wait_feedback_stim = stop_stimulus
            wait_for_poke_out_stim = stop_stimulus
        elif task_parameters.StimAfterPokeOut == StimAfterPokeOut.UntilFeedbackEnd:
            wait_for_decision_stim = cont_deliver_stimulus
            wait_feedback_stim = cont_deliver_stimulus
            wait_for_poke_out_stim = stop_stimulus
        elif task_parameters.StimAfterPokeOut == StimAfterPokeOut.UntilEndofTrial:
            wait_for_decision_stim = cont_deliver_stimulus
            wait_feedback_stim = cont_deliver_stimulus
            wait_for_poke_out_stim = cont_deliver_stimulus
        else:
            error('Unexpected StimAfterPokeOut Option')

        # Valve opening is a bitmap. Open each valve separately by raising 2 to
        # the power of port number - 1
        # left_valve = 2 ** (left_port - 1)
        # center_valve = 2 ** (center_port - 1)
        # right_valve = 2 ** (right_port - 1)
        left_valve = left_port
        center_valve = center_port
        right_valve = right_port

        right_valve_time = GetValveTimes(
            data.Custom.Trials.RewardMagnitude[i_trial][0], left_port)
        center_valve_time = GetValveTimes(
            data.Custom.Trials.CenterPortRewAmount[i_trial], center_port)
        right_valve_time = GetValveTimes(
            data.Custom.Trials.RewardMagnitude[i_trial][1], right_port)

        rewarded_port = iff(is_left_rewarded, left_port, right_port)
        rewarded_port_pwm = iff(is_left_rewarded, left_pwm, right_pwm)
        incorrect_consequence = iff(
            not task_parameters.HabituateIgnoreIncorrect,
            str(MatrixState.WaitForPunishStart),
            str(MatrixState.RegisterWrongWaitCorrect))
        left_action_state = iff(is_left_rewarded, str(
            MatrixState.WaitForRewardStart), incorrect_consequence)
        left_action_state = iff(is_left_rewarded, incorrect_consequence, str(
            MatrixState.WaitForRewardStart))
        reward_in = iff(is_left_rewarded, left_port_in, right_port_in)
        reward_out = iff(is_left_rewarded, left_port_out, right_port_out)
        punish_in = iff(is_left_rewarded, right_port_in, left_port_in)
        punish_out = iff(is_left_rewarded, right_port_out, left_port_out)
        valve_time = iff(is_left_rewarded, right_valve_time, right_valve_time)
        valve_code = iff(is_left_rewarded, left_valve, right_valve)

        # Check if to play beep at end of minimum sampling
        min_sample_beep = iff(task_parameters.BeepAfterMinSampling, [
                            ('SoftCode', 12)], [])
        min_sample_beep_duration = iff(
            task_parameters.BeepAfterMinSampling, 0.01, 0)
        # GUI option RewardAfterMinSampling
        # If center - reward is enabled, then a reward is given once MinSample
        # is over and no further sampling is given.
        reward_center_port = iff(task_parameters.RewardAfterMinSampling,
                               [('Valve', center_valve)] + stop_stimulus,
                               cont_deliver_stimulus)
        timer_cprd = iff(
            task_parameters.RewardAfterMinSampling, center_valve_time,
            task_parameters.StimulusTime - task_parameters.MinSample)

        # White Noise played as Error Feedback
        error_feedback = iff(task_parameters.PlayNoiseforError, [(
            'SoftCode', 11)], [])

        # CatchTrial
        feedback_delay_correct = iff(data.Custom.Trials.CatchTrial[
            i_trial], Const.FEEDBACK_CATCH_MAX_SEC,
            max(task_parameters.FeedbackDelay,0.01))

        # GUI option CatchError
        feedback_delay_punish = iff(task_parameters.CatchError,
                                  Const.FEEDBACK_CATCH_MAX_SEC,
                                  max(task_parameters.FeedbackDelay,0.01))
        skipped_feeback_signal = iff(
            task_parameters.CatchError, [], error_feedback)

        #Incorrect Timeout
        incorrect_timeout = iff(not task_parameters.PCTimeout,
                               task_parameters.TimeOutIncorrectChoice
                               + task_parameters.ITI,
                               .01)

        # Incorrect Choice signal
        if task_parameters.IncorrectChoiceSignalType == \
                IncorrectChoiceSignalType.NoisePulsePal:
            punishment_duration = 0.01
            incorrect_choice_signal = [('SoftCode', 11)]
        elif task_parameters.IncorrectChoiceSignalType == \
                IncorrectChoiceSignalType.BeepOnWire_1:
            punishment_duration = 0.25
            incorrect_choice_signal = [('Wire1', 1)]
        elif task_parameters.IncorrectChoiceSignalType == \
                IncorrectChoiceSignalType.PortLED:
            punishment_duration = 0.1
            incorrect_choice_signal = [
                (pwm_str(left_port), left_pwm),
                (pwm_str(center_port), center_pwm),
                (pwm_str(right_port), right_pwm)
            ]
        elif task_parameters.IncorrectChoiceSignalType == \
                IncorrectChoiceSignalType.none:
            punishment_duration = 0.01
            incorrect_choice_signal = []
        else:
            error('Unexpected IncorrectChoiceSignalType value')

        # ITI signal
        if task_parameters.ITISignalType == ITISignalType.Beep:
            iti_signal_duration = 0.01
            iti_signal = [('SoftCode', 12)]
        elif task_parameters.ITISignalType == ITISignalType.PortLED:
            iti_signal_duration = 0.1
            iti_signal = [
                (pwm_str(left_port), left_pwm),
                (pwm_str(center_port), center_pwm),
                (pwm_str(right_port), right_pwm)
            ]
        elif task_parameters.ITISignalType == ITISignalType.none:
            iti_signal_duration = 0.01
            iti_signal = []
        else:
            error('Unexpected ITISignalType value')

        # Wire1 settings
        wire1_out_error = iff(task_parameters.Wire1VideoTrigger, [(
                            'Wire2', 2)], [])
        wire1_out_correct_condition = task_parameters.Wire1VideoTrigger and \
            data.Custom.Trials.CatchTrial[i_trial]
        wire1_out_correct = iff(wire1_out_correct_condition,
                              [('Wire2', 2)], [])

        # LED on the side lateral port to cue the rewarded side at the
        # beginning of the training. On auditory discrimination task, both
        # lateral ports are illuminated after end of stimulus delivery.
        if data.Custom.Trials.ForcedLEDTrial[i_trial]:
            extended_stimulus = [(pwm_str(rewarded_port), rewarded_port_pwm)]
        elif task_parameters.ExperimentType == ExperimentType.Auditory:
            extended_stimulus = [
                (pwm_str(left_port), left_pwm),
                (pwm_str(right_port), right_pwm)
            ]
        else:
            extended_stimulus = []

        pc_timeout = task_parameters.PCTimeout
        # Build state matrix
        self.set_global_timer(1, task_parameters.ChoiceDeadline)
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
                       state_timer=iff(task_parameters.PreStimDelayCntrReward,
                                       GetValveTimes(task_parameters.PreStimDelayCntrReward,
                                       center_port), 0.01),
                       state_change_conditions={
                           Bpod.Events.Tup:str(MatrixState.TriggerWaitForStimulus)},
                       output_actions=iff(task_parameters.PreStimDelayCntrReward,
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
                                       task_parameters.StimDelay
                                       - wire_ttl_duration),
                       state_change_conditions={
                           center_port_out: str(MatrixState.StimDelayGrace),
                           Bpod.Events.Tup: str(MatrixState.stimulus_delivery)},
                        output_actions= [])
        self.add_state(state_name=str(MatrixState.StimDelayGrace),
                       state_timer=task_parameters.StimDelayGrace,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.broke_fixation),
                           center_port_in: str(MatrixState.TriggerWaitForStimulus)},
                       output_actions= [])
        self.add_state(state_name=str(MatrixState.broke_fixation),
                       state_timer=iff(not pc_timeout,
                                       task_parameters.TimeOutBrokeFixation,
                                       0.01),
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.ITI)},
                       output_actions=error_feedback)
        self.add_state(state_name=str(MatrixState.stimulus_delivery),
                       state_timer=task_parameters.MinSample
                                    - min_sample_beep_duration
                                    - timer_cprd,
                       state_change_conditions={
                           center_port_out: str(MatrixState.early_withdrawal),
                           Bpod.Events.Tup: str(MatrixState.BeepMinSampling)},
                       output_actions=delivery_stimulus)
        self.add_state(state_name=str(MatrixState.early_withdrawal),
                       state_timer=0,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.timeOut_EarlyWithdrawal)},
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
                       state_timer= max(0,task_parameters.StimulusTime
                                        - task_parameters.MinSample
                                        - timer_cprd
                                        - min_sample_beep_duration),
                       state_change_conditions={
                           center_port_out: str(MatrixState.TriggerWaitChoiceTimer),
                           Bpod.Events.Tup: str(MatrixState.WaitCenterPortOut)},
                       output_actions=cont_deliver_stimulus)
        # TODO: Stop stimulus is fired twice in case of center reward and then
        # wait for choice. Fix it such that it'll be always fired once.
        self.add_state(state_name=str(MatrixState.TriggerWaitChoiceTimer),
                       state_timer=0,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitForChoice)},
                       output_actions=(wait_for_decision_stim + extended_stimulus
                                       + [('GlobalTimerTrig', EncTrig(1))]))
        self.add_state(state_name=str(MatrixState.WaitCenterPortOut),
                       state_timer=0,
                       state_change_conditions={
                           center_port_out: str(MatrixState.WaitForChoice),
                           left_port_in: left_action_state,
                           right_port_in: left_action_state,
                           'GlobalTimer1_End': str(MatrixState.timeOut_missed_choice
                                    )},
                       output_actions=(wait_for_decision_stim + extended_stimulus
                                       + [('GlobalTimerTrig', EncTrig(1))]))
        self.add_state(state_name=str(MatrixState.WaitForChoice),
                       state_timer=0,
                       state_change_conditions={
                           left_port_in: left_action_state,
                           right_port_in: left_action_state,
                           'GlobalTimer1_End': str(MatrixState.timeOut_missed_choice)},
                       output_actions=(wait_for_decision_stim + extended_stimulus))
        self.add_state(state_name=str(MatrixState.WaitForRewardStart),
                       state_timer=0,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitForReward)},
                       output_actions=(wire1_out_correct + wait_feedback_stim
                                       + [('GlobalTimerTrig', EncTrig(2))]))
        self.add_state(state_name=str(MatrixState.WaitForReward),
                       state_timer=0,
                       state_change_conditions={
                           'GlobalTimer2_End': str(MatrixState.Reward),
                           reward_out: str(MatrixState.RewardGrace)},
                           output_actions=wait_feedback_stim)
        self.add_state(state_name=str(MatrixState.RewardGrace),
                       state_timer=task_parameters.FeedbackDelayGrace,
                       state_change_conditions={
                           reward_in: str(MatrixState.WaitForReward),
                           Bpod.Events.Tup: str(MatrixState.timeOut_SkippedFeedback),
                           'GlobalTimer2_End': str(MatrixState.timeOut_SkippedFeedback),
                           center_port_in: str(MatrixState.timeOut_SkippedFeedback),
                           punish_in: str(MatrixState.timeOut_SkippedFeedback)},
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
                       output_actions= ([('GlobalTimerTrig', EncTrig(5))] + wait_for_poke_out_stim) )
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
                                       + [('GlobalTimerTrig', EncTrig(3))]))
        self.add_state(state_name=str(MatrixState.WaitForPunish),
                       state_timer=0,
                       state_change_conditions={
                           'GlobalTimer3_End': str(MatrixState.Punishment),
                           punish_out: str(MatrixState.PunishGrace)},
                       output_actions=wait_feedback_stim)
        self.add_state(state_name=str(MatrixState.PunishGrace),
                       state_timer=task_parameters.FeedbackDelayGrace,
                       state_change_conditions={
                           punish_in: str(MatrixState.WaitForPunish),
                           Bpod.Events.Tup: str(MatrixState.timeOut_SkippedFeedback),
                           'GlobalTimer3_End': str(MatrixState.timeOut_SkippedFeedback),
                           center_port_in: str(MatrixState.timeOut_SkippedFeedback),
                           reward_in: str(MatrixState.timeOut_SkippedFeedback)},
                       output_actions=wait_feedback_stim)
        self.add_state(state_name=str(MatrixState.Punishment),
                       state_timer=punishment_duration,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.WaitPunishOut),
                           punish_out: str(MatrixState.timeOut_IncorrectChoice)},
                       output_actions=(incorrect_choice_signal + wait_feedback_stim))
        self.add_state(state_name=str(MatrixState.WaitPunishOut),
                       state_timer= 1, #TODO: = task_parameters.waitfinalpokeoutsec
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.timeOut_IncorrectChoice),
                           punish_out: str(MatrixState.timeOut_IncorrectChoice)},
                       output_actions= ([('GlobalTimerTrig', EncTrig(4))] + wait_for_poke_out_stim))
        self.add_state(state_name=str(MatrixState.timeOut_EarlyWithdrawal),
                       state_timer=LED_error_rate,
                       state_change_conditions={
                           'SoftCode1': str(MatrixState.ITI),
                           Bpod.Events.Tup: str(MatrixState.timeOut_EarlyWithdrawalFlashOn)},
                       output_actions=(stop_stimulus + error_feedback + [('SoftCode',2)]))
        self.add_state(state_name=str(MatrixState.timeOut_EarlyWithdrawalFlashOn),
                       state_timer=LED_error_rate,
                       state_change_conditions={
                           'SoftCode1': str(MatrixState.ITI),
                           Bpod.Events.Tup: str(MatrixState.timeOut_EarlyWithdrawal)},
                       output_actions=(stop_stimulus + error_feedback +
                         [(pwm_str(left_port), left_pwm),
                          (pwm_str(right_port), right_pwm)]))
        self.add_state(state_name=str(MatrixState.timeOut_IncorrectChoice),
                       state_timer=0,
                       state_change_conditions={
                           'Condition4': str(MatrixState.ext_ITI)},
                       output_actions= stop_stimulus)
        self.add_state(state_name=str(MatrixState.timeOut_SkippedFeedback),
                       state_timer=iff(not pc_timeout,
                                       task_parameters.TimeOutSkippedFeedback,
                                       0.01),
                       state_change_conditions={
                          Bpod.Events.Tup: str(MatrixState.ITI)},# TODO: See how to get around this if pc_timeout
                       output_actions=(stop_stimulus + skipped_feeback_signal))
        self.add_state(state_name=str(MatrixState.timeOut_missed_choice),
                       state_timer=iff(not pc_timeout,
                                       task_parameters.TimeOutMissedChoice,
                                       0.01),
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.ITI)},
                       output_actions=(stop_stimulus + error_feedback))
        self.add_state(state_name=str(MatrixState.ITI),
                       state_timer=wire_ttl_duration,
                       state_change_conditions={
                           Bpod.Events.Tup: str(MatrixState.ext_ITI)},
                       output_actions=([('GlobalTimerTrig', EncTrig(5))]+ stop_stimulus))
        self.add_state(state_name=str(MatrixState.ext_ITI),
                       state_timer=iff(not pc_timeout,
                                       task_parameters.ITI,
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

        if data.Custom.Trials.OptoEnabled[i_trial]:
            # Convert seconds to millis as we will send ints to Arduino
            opto_delay = np.array(
                [task_parameters.OptoStartDelay * 1000], dtype=np.uint32)
            opto_delay = opto_delay.view(np.uint8)
            opto_time = np.array(
                [task_parameters.OptoMaxTime * 1000], dtype=np.uint32)
            opto_time = opto_time.view(np.uint8)
            if not EMULATOR_MODE or hasattr(PluginSerialPorts, 'OptoSerial'):
                fwrite(PluginSerialPorts.OptoSerial, opto_delay, 'int8')
                fwrite(PluginSerialPorts.OptoSerial, opto_time, 'int8')
            opto_start_event_idx = \
                self.hardware.channels.output_channel_names.index('Wire3')
            opto_stop_event_idx = \
                self.hardware.channels.output_channel_names.index('Wire4')
            tuples = [
                (str(task_parameters.OptoStartState1), opto_start_event_idx),
                (str(task_parameters.OptoEndState1), opto_stop_event_idx),
                (str(task_parameters.OptoEndState2), opto_stop_event_idx),
                (str(MatrixState.ext_ITI), opto_stop_event_idx)
            ]
            for state_name, event_idx in tuples:
                trgt_state_num = self.state_names.index(state_name)
                self.output_matrix[trgt_state_num][event_idx] = 1
