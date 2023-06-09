import logging
import math
import numpy as np
import random

import settings

logger = logging.getLogger(__name__)

floor = math.floor
mod = np.remainder
round = np.around
rand = np.random.rand
randi = np.random.randint
random_unif = np.random.uniform
randperm = np.random.permutation
diff = np.diff
polyval = np.polyval
betarnd = np.random.beta
# TODO: verify correctness that randsample is equivalent to random.choices
randsample = random.choices
concat = np.concatenate
ones = np.ones
ceil = np.ceil
zeros = np.zeros
randsample = np.random.choice


def iff(condition, value1, value2):
    return value1 if condition else value2


def dec2bin(decimal):
    return f'{160:3b}'.replace(' ', '0')


def GetCatchStimIdx(stimulus_omega):
    # stimulus_omega is between 0 and 1, we break it down to bins of 20
    def calc_catch_stim_idx(omega):
        return round(omega * 20) + 1
    if isinstance(stimulus_omega, list):
        catch_stim_idx = [calc_catch_stim_idx(
            omega) for omega in stimulus_omega]
    else:
        catch_stim_idx = calc_catch_stim_idx(stimulus_omega)
    return catch_stim_idx


def TruncatedExponential(min_value, max_value, tau):
    if min_value == max_value == 0:
        raise ValueError('Invalid value 0 for min_value and max_value.')
    # Initialize to a large value
    exp = max_value + 1
    # sample until in range
    while exp > (max_value - min_value):
        exp = random.expovariate(tau)
    # add the offset
    exp += min_value
    return exp


def EncTrig(trigger_id):
    # Provides V1 & V2 compatibility
    return iff(settings.IS_V2, dec2bin(trigger_id), trigger_id)


def CalcAudClickTrain(data, trial_num):
    return 1


def CalcLightIntensity(data, trial_num):
    data.Custom.Trials.LightIntensityLeft[trial_num] = \
        round(data.Custom.Trials.StimulusOmega[trial_num] * 100)
    data.Custom.Trials.LightIntensityRight[trial_num] = \
        round((1 - data.Custom.Trials.StimulusOmega[trial_num]) * 100)
    dv = (data.Custom.Trials.StimulusOmega[trial_num] * 2) - 1
    return dv


def CalcGratingOrientation(data, trial_num):
    return 1


def CalcDotsCoherence(data, trial_num):
    return 1


class GetValveTimesError(Exception):
    pass


def error(message):
    logger.error(message)
    raise GetValveTimesError(message)


class LiquidCalClass:
    def __init__(self, Table, Coeffs):
        self.Table = Table
        self.Coeffs = Coeffs


class CalibrationTables:
    DEFAULT_TABLES = [
        [
            [15.0000, 0],
            [20.0000, 0.1700],
            [50.0000, 1.3500],
            [50.0000, 1.3100],
            [30.0000, 0.5500],
            [75.0000, 2.6350],
            [100.0000, 3.8200],
            [150.0000, 6.5900],
        ],
        [
            [10.0000, 0],
            [20.0000, 0.2050],
            [50.0000, 1.1800],
            [50.0000, 1.0850],
            [30.0000, 0.4600],
            [75.0000, 2.2000],
            [100.0000, 3.3600],
            [150.0000, 5.6300],
        ],
        [
            [10.0000, 0],
            [20.0000, 0.4900],
            [50.0000, 1.5200],
            [50.0000, 1.2950],
            [30.0000, 0.6200],
            [75.0000, 2.7750],
            [100.0000, 4.1800],
            [150.0000, 6.6500],
        ],
        [], [], [], [], []
    ]
    COEFFS = [
        [0.6847, 24.7278, 16.3721],
        [1.1799, 30.5735, 14.1329],
        [0.6150, 24.5236, 12.5769],
        [0], [0], [0], [0], [0]
    ]

    LiquidCal = [LiquidCalClass(table, coeffs)
                 for table, coeffs in zip(DEFAULT_TABLES, COEFFS)]


def GetValveTimes(LiquidAmount, TargetValves):
    if isinstance(TargetValves, int):
        TargetValves = [TargetValves]
    nValves = len(TargetValves)
    ValveTimes = [0] * nValves
    for x in range(nValves):
        ValidTable = True
        TargetValveIdx = TargetValves[x] - 1
        CurrentTable = CalibrationTables.LiquidCal[
            TargetValveIdx].Table
        if CurrentTable:
            ValveDurations = [row[0] for row in CurrentTable]
            nMeasurements = len(ValveDurations)
            if nMeasurements < 2:
                ValidTable = False
                error('Not enough liquid calibration measurements exist for'
                      f'valve {TargetValves[x]}. Bpod needs at least 3'
                      'measurements.')
        else:
            ValidTable = False
            error('Not enough liquid calibration measurements exist for valve '
                  f'{TargetValves[x]}. Bpod needs at least 3 measurements.')
        if ValidTable:
            ValveTimes[x] = polyval(CalibrationTables.LiquidCal[
                TargetValveIdx].Coeffs, LiquidAmount)
            if ValveTimes[x] is None:
                ValveTimes[x] = 0
            if any([(valve_time < 0) for valve_time in ValveTimes]):
                error(f'Wrong liquid calibration for valve {TargetValves[x]}.'
                      'Negative open time.')
        ValveTimes[x] /= 1000
    result = ValveTimes[0] if nValves == 1 else ValveTimes
    return result

def ControlledRandom(probability,_NumTrialsToGenerate):
        _NumPositiveTrials = _NumTrialsToGenerate * probability
        OneZeroArr = concat((ones(int(ceil(_NumPositiveTrials))),
                             zeros(int(ceil(_NumTrialsToGenerate-_NumPositiveTrials)))))
        OneZeroArr = randperm(len(OneZeroArr))
        OneZeroArr = OneZeroArr[:_NumTrialsToGenerate].astype(int).tolist()
        return OneZeroArr