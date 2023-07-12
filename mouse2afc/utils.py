import logging
import math
import random
import numpy as np

from mouse2afc import settings

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
shuffle = np.random.shuffle
isnan = np.isnan


def iff(condition, value1, value2):
    return value1 if condition else value2


def dec_2_bin(decimal):
    return f'{160:3b}'.replace(' ', '0')


def get_catch_stim_idx(stimulus_omega):
    # stimulus_omega is between 0 and 1, we break it down to bins of 20
    def calc_catch_stim_idx(omega):
        return round(omega * 20) + 1
    if isinstance(stimulus_omega, list):
        catch_stim_idx = [calc_catch_stim_idx(
            omega) for omega in stimulus_omega]
    else:
        catch_stim_idx = calc_catch_stim_idx(stimulus_omega)
    return catch_stim_idx


def truncated_exponential(min_value, max_value, tau):
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


def enc_trig(trigger_id):
    # Provides V1 & V2 compatibility
    return iff(settings.IS_V2, dec_2_bin(trigger_id), trigger_id)


def calc_aud_click_train(data, trial_num):
    return 1


def calc_light_intensity(data, trial_num):
    data.trials.light_intensity_left[trial_num] = \
        round(data.trials.stimulus_omega[trial_num] * 100)
    data.trials.light_intensity_right[trial_num] = \
        round((1 - data.trials.stimulus_omega[trial_num]) * 100)
    dv = (data.trials.stimulus_omega[trial_num] * 2) - 1
    return dv


def calc_grating_orientation(data, trial_num):
    return 1


def calc_dots_coherence(data, trial_num):
    return 1


def error(message):
    logger.error(message)
    raise GetValveTimesError(message)


class GetValveTimesError(Exception):
    pass


class LiquidCalClass:
    def __init__(self, table, coeffs):
        self.table = table
        self.coeffs = coeffs


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


def get_valve_times(liquid_amount, target_valves):
    if isinstance(target_valves, int):
        target_valves = [target_valves]
    n_valves = len(target_valves)
    valve_times = [0] * n_valves
    for x in range(n_valves):
        valid_table = True
        target_valve_idx = target_valves[x] - 1
        current_table = CalibrationTables.LiquidCal[
            target_valve_idx].table
        if current_table:
            valve_durations = [row[0] for row in current_table]
            n_measurements = len(valve_durations)
            if n_measurements < 2:
                valid_table = False
                error('Not enough liquid calibration measurements exist for'
                      f'valve {target_valves[x]}. Bpod needs at least 3'
                      'measurements.')
        else:
            valid_table = False
            error('Not enough liquid calibration measurements exist for valve '
                  f'{target_valves[x]}. Bpod needs at least 3 measurements.')
        if valid_table:
            valve_times[x] = polyval(CalibrationTables.LiquidCal[
                target_valve_idx].coeffs, liquid_amount)
            if valve_times[x] is None:
                valve_times[x] = 0
            if any([(valve_time < 0) for valve_time in valve_times]):
                error(f'Wrong liquid calibration for valve {target_valves[x]}.'
                      'Negative open time.')
        valve_times[x] /= 1000
    result = valve_times[0] if n_valves == 1 else valve_times
    return result

def controlled_random(probability,_num_trials_to_generate):
    " Returns an array of 1's and 0's of length _num_trials_to_generate "
    # The ratio of 1's:0's is = probability
    num_positive_trials = _num_trials_to_generate * probability
    one_zero_arr = concat((ones(int(ceil(num_positive_trials))),
                            zeros(int(ceil(_num_trials_to_generate-num_positive_trials)))))
    shuffle(one_zero_arr)
    one_zero_arr = one_zero_arr[:_num_trials_to_generate].astype(int).tolist()
    return one_zero_arr
