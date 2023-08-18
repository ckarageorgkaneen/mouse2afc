"This file defines the default values which populate the task parameters gui"
import math

from  mouse2afc.definitions.brain_region import BrainRegion
from  mouse2afc.definitions.experiment import ExperimentType
from  mouse2afc.definitions.feedback_delay_selection import FeedbackDelaySelection
from  mouse2afc.definitions.incorrect_choice_signal_type import IncorrectChoiceSignalType
from  mouse2afc.definitions.iti_signal_type import ITISignalType
from  mouse2afc.definitions.matrix_state import MatrixState
from  mouse2afc.definitions.min_sample_type import MinSampleType
from  mouse2afc.definitions.mouse_state import MouseState
from  mouse2afc.definitions.stimulus_selection_criteria import StimulusSelectionCriteria
from  mouse2afc.definitions.ttl_wire_usage import TTLWireUsage
from  mouse2afc.definitions.visual_stim_angle import VisualStimAngle
from  mouse2afc.definitions.stim_after_poke_out import StimAfterPokeOut

from mouse2afc.task_parameters import TaskParametersGUITable

from mouse2afc.utils import round

all_preformance = '(Calc. after 1st trial)'
beep_after_min_sampling = False
beta_dist_alpha_n_beta = 0.3
calc_left_bias = 0.5
catch_error = False
center_poke_atten_prcnt = 100
center_port_rew_amount = 0.6
choice_deadline = 10
computer_name = None
correct_bias = True
current_stim = 0
experiment_type = ExperimentType.light_intensity
secondary_experiment_type = ExperimentType.no_stimulus
feedback_delay_max = 1.5
feedback_delay_min = 0.5
feedback_delay = feedback_delay_min
feedback_delay_incr = 0.01
feedback_delay_decr = 0.01
feedback_delay_tau = 0.1
feedback_delay_grace = 0.4
feedback_delay_selection = FeedbackDelaySelection.none
gui_ver = 29
habituate_ignore_incorrect = 0
iti = 1
iti_signal_type = ITISignalType.none
incorrect_choice_signal_type = IncorrectChoiceSignalType.beep_on_wire1
is_catch = False
is_opto_trial = False
left_bias = 0.5
left_bias_val = left_bias
left_poke_atten_prcnt = 75
min_sample_max = 0.2
min_sample_min = 0.2
min_sample = min_sample_min
min_sample_decr = 0.01
min_sample_incr = 0.02
min_sample_num_interval = 1
min_sample_rand_prob = 0
min_sample_type = MinSampleType.auto_incr
mouse_state = MouseState.freely_moving
mouse_weight = None
_omega_stim_pct_values = list(range(100, 50, -5))
_len_omega = len(_omega_stim_pct_values)
_omega_prob = [_len_omega - i - 1 for i in range(_len_omega)]
_omega_rdk = [(prob - 50) * 2 for prob in _omega_stim_pct_values]
omega_table = TaskParametersGUITable(
    headers=['Stim %', 'RDK Coh.', 'P(a)'],
    omega=_omega_stim_pct_values,
    omega_prob=_omega_prob,
    rdk=_omega_rdk)
opto_brain_region = BrainRegion.V1_L
opto_end_state_1 = MatrixState.WaitCenterPortOut
opto_end_state_2 = MatrixState.WaitForChoice
opto_max_time = 10
opto_or_2_photon = TTLWireUsage.optogenetics
opto_prob = 0
opto_start_delay = 0
opto_start_state_1 = MatrixState.StimulusDelivery
pc_timeout = True
percent_50_fifty = 0
percent_catch = 0
percent_forced_led_trial = 0
performance = '(Calc. after 1st trial)'
play_noise_for_error = 0
port_led_to_cue_reward = False
ports_lmr_air = 123568
pre_stim_delay_cntr_reward = 0
reward_after_min_sampling = True
reward_amount = 5.5
right_poke_atten_prcnt = 75
show_feedback = 1
show_fix = 1
show_psyc_stim = 1
show_st = 1
show_trial_rate = 1
show_vevaiometric = 1
start_easy_trials = 10
stim_after_poke_out = StimAfterPokeOut.until_feedback_start
stim_delay_max = 0
stim_delay_min = 0
stim_delay = stim_delay_min
stim_delay_auto_increment = 0
stim_delay_decr = 0.01
stim_delay_incr = 0.01
stim_delay_grace = 0.1
stimulus_selection_criteria = StimulusSelectionCriteria.discrete_pairs
stimulus_time = 0.3
sum_rates = 100
table_note = 'Edit Stim % to update RDK'
timeout_broke_fixation = 0
timeout_early_withdrawal = 0
timeout_incorrect_choice = 2
timeout_missed_choice = 1
timeout_skipped_feedback = 0
vevaiometric_min_wt = 0.5
vevaiometric_n_bin = 8
vevaiometric_show_points = 1
vevaiometric_y_lim = 20
visual_stim_angle_port_left = VisualStimAngle.degrees_270
visual_stim_angle_port_right = VisualStimAngle.degrees_90
wire1_video_trigger = False
aperture_size_height = 36
aperture_size_width = 36
center_x = 0
center_y = 0
circle_area = math.pi * ((aperture_size_width / 2) ** 2)
cycles_per_second_drift = 5
dot_lifetime_secs = 1
dot_size_in_degs = 2
dot_speed_degs_per_sec = 25
draw_ratio = 0.2
gabor_size_factor = 1.2
gaussian_filter_ratio = 0.1
n_dots = round(circle_area * 0.05)
num_cycles = 20
phase = 0  # Phase of the wave, goes between 0 to 360
screen_dist_cm = 30
screen_width_cm = 20
