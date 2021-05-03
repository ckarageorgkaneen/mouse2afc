import math

from definitions.brain_region import BrainRegion
from definitions.experiment import ExperimentType
from definitions.feedback_delay_selection import FeedbackDelaySelection
from definitions.incorrect_choice_signal_type import IncorrectChoiceSignalType
from definitions.iti_signal_type import ITISignalType
from definitions.matrix_state import MatrixState
from definitions.min_sample_type import MinSampleType
from definitions.mouse_state import MouseState
from definitions.stimulus_selection_criteria import StimulusSelectionCriteria
from definitions.ttl_wire_usage import TTLWireUsage
from definitions.visual_stim_angle import VisualStimAngle

from utils import round

AllPerformance = '(Calc. after 1st trial)'
BeepAfterMinSampling = False
BetaDistAlphaNBeta = 0.3
CalcLeftBias = 0.5
CatchError = False
CenterPokeAttenPrcnt = 95
CenterPortRewAmount = 0.5
ChoiceDeadLine = 20
ComputerName = None
CorrectBias = False
CurrentStim = 0
CutAirReward = False
CutAirSampling = True
CutAirStimDelay = True
ExperimentType = ExperimentType.LightIntensity
FeedbackDelayMax = 1.5
FeedbackDelayMin = 0.5
FeedbackDelay = FeedbackDelayMin
FeedbackDelayIncr = 0.01
FeedbackDelayDecr = 0.01
FeedbackDelayTau = 0.1
FeedbackDelayGrace = 0.4
FeedbackDelaySelection = FeedbackDelaySelection.Fix
GUIVer = 29
HabituateIgnoreIncorrect = 0
ITI = 0
ITISignalType = ITISignalType.none
IncorrectChoiceSignalType = IncorrectChoiceSignalType.BeepOnWire_1
IsCatch = False
IsOptoTrial = False
LeftBias = 0.5
LeftBiasVal = LeftBias
LeftPokeAttenPrcnt = 73
MinSampleMax = 0
MinSampleMin = 0
MinSample = MinSampleMin
MinSampleDecr = 0.02
MinSampleIncr = 0.05
MinSampleNumInterval = 1
MinSampleRandProb = 0
MinSampleType = MinSampleType.AutoIncr
MouseState = MouseState.FreelyMoving
MouseWeight = None
_omega_stim_pct_values = list(range(100, 50, -5))
_len_omega = len(_omega_stim_pct_values)
_omega_prob = [_len_omega - i - 1 for i in range(_len_omega)]
_omega_rdk = [(prob - 50) * 2 for prob in _omega_stim_pct_values]
OmegaTable = {
    'Omega': {
        'ColumnName': 'Stim %',
        'Value': _omega_stim_pct_values,
    },
    'OmegaProb': {
        'ColumnName': 'P(a)',
        'Value': _omega_prob,
    },
    'RDK': {
        'ColumnName': 'RDK Coh.',
        'Value': _omega_rdk
    }
}
OptoBrainRegion = BrainRegion.V1_L
OptoEndState1 = MatrixState.WaitCenterPortOut
OptoEndState2 = MatrixState.WaitForChoice
OptoMaxTime = 10
OptoOr2P = TTLWireUsage.Optogenetics
OptoProb = 0
OptoStartDelay = 0
OptoStartState1 = MatrixState.stimulus_delivery
PCTimeout = True
Percent50Fifty = 0
PercentCatch = 0
PercentForcedLEDTrial = 0
Performance = '(Calc. after 1st trial)'
PlayNoiseforError = 0
PortLEDtoCueReward = False
Ports_LMRAir = 1238
PreStimuDelayCntrReward = 0
RewardAfterMinSampling = False
RewardAmount = 5
RightPokeAttenPrcnt = 73
ShowFeedback = 1
ShowFix = 1
ShowPsycStim = 1
ShowST = 1
ShowTrialRate = 1
ShowVevaiometric = 1
StartEasyTrials = 10
StimAfterPokeOut = False
StimDelayMax = 0.6
StimDelayMin = 0.3
StimDelay = StimDelayMin
StimDelayAutoincrement = 0
StimDelayDecr = 0.01
StimDelayIncr = 0.01
StimDelayGrace = 0.1
StimulusSelectionCriteria = StimulusSelectionCriteria.DiscretePairs
StimulusTime = 0.3
SumRates = 100
TableNote = 'Edit Stim % to update RDK'
TimeOutBrokeFixation = 0
TimeOutEarlyWithdrawal = 0
TimeOutIncorrectChoice = 0
TimeOutMissedChoice = 0
TimeOutSkippedFeedback = 0
VevaiometricMinWT = 0.5
VevaiometricNBin = 8
VevaiometricShowPoints = 1
VevaiometricYLim = 20
VisualStimAnglePortLeft = VisualStimAngle.Degrees270
VisualStimAnglePortRight = VisualStimAngle.Degrees90
Wire1VideoTrigger = False
ApertureSizeHeight = 36
ApertureSizeWidth = 36
CenterX = 0
CenterY = 0
CircleArea = math.pi * ((ApertureSizeWidth / 2) ** 2)
CyclesPerSecondDrift = 5
DotLifetimeSecs = 1
DotSizeInDegs = 2
DotSpeedDegsPerSec = 25
DrawRatio = 0.2
GaborSizeFactor = 1.2
GaussianFilterRatio = 0.1
nDots = round(CircleArea * 0.05)
NumCycles = 20
Phase = 0  # Phase of the wave, goes between 0 to 360
ScreenDistCm = 30
ScreenWidthCm = 20
