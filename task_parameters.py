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


class Figures:
    class Position:
        def __init__(self, Position):
            self.Position = Position

    def __init__(self):
        self.OutcomePlot = self.Position([200, 200, 1000, 400])
        self.ParameterGUI = self.Position([9, 454, 1474, 562])


class GUITabs:
    General = ['CurrentTrial', 'AirControl',
               'General', 'FeedbackDelay', 'StimDelay']
    Opto = ['Optogenetics']
    Plots = ['ShowPlots', 'Vevaiometric']
    Sampling = ['CurrentTrial', 'LightIntensity',
                'Auditory', 'Sampling', 'StimulusSelection']
    Visual = ['CurrentTrial', 'Grating',
              'RandomDots', 'VisualGeneral']


class GUIPanels:
    AirControl = ['CutAirStimDelay', 'CutAirReward', 'CutAirSampling']
    Auditory = 'SumRates'
    CurrentTrial = ['MouseState', 'MouseWeight', 'StimDelay', 'MinSample',
                    'CurrentStim', 'CalcLeftBias', 'FeedbackDelay', 'IsCatch',
                    'IsOptoTrial', 'Performance', 'AllPerformance']
    FeedbackDelay = ['FeedbackDelaySelection', 'FeedbackDelayMin',
                     'FeedbackDelayMax', 'FeedbackDelayIncr',
                     'FeedbackDelayDecr', 'FeedbackDelayTau',
                     'FeedbackDelayGrace', 'IncorrectChoiceSignalType',
                     'ITISignalType']
    General = ['ExperimentType', 'ITI', 'RewardAmount', 'ChoiceDeadLine',
               'TimeOutIncorrectChoice', 'TimeOutBrokeFixation',
               'TimeOutEarlyWithdrawal', 'TimeOutMissedChoice',
               'TimeOutSkippedFeedback', 'HabituateIgnoreIncorrect',
               'PlayNoiseforError', 'PCTimeout', 'StartEasyTrials',
               'Percent50Fifty', 'PercentCatch', 'CatchError', 'Ports_LMRAir',
               'Wire1VideoTrigger']
    Grating = ['gaborSizeFactor', 'phase', 'numCycles',
               'cyclesPerSecondDrift', 'gaussianFilterRatio']
    LightIntensity = ['LeftPokeAttenPrcnt', 'CenterPokeAttenPrcnt',
                      'RightPokeAttenPrcnt', 'StimAfterPokeOut',
                      'BeepAfterMinSampling']
    Optogenetics = ['OptoProb', 'OptoOr2P', 'OptoStartState1',
                    'OptoStartDelay', 'OptoMaxTime', 'OptoEndState1',
                    'OptoEndState2', 'OptoBrainRegion', 'IsOptoTrial']
    RandomDots = ['drawRatio', 'circleArea', 'nDots',
                  'dotSizeInDegs', 'dotSpeedDegsPerSec', 'dotLifetimeSecs']
    Sampling = ['RewardAfterMinSampling', 'CenterPortRewAmount',
                'MinSampleMin', 'MinSampleMax', 'MinSampleType',
                'MinSampleIncr', 'MinSampleDecr', 'MinSampleNumInterval',
                'MinSampleRandProb', 'StimulusTime', 'PortLEDtoCueReward',
                'PercentForcedLEDTrial']
    ShowPlots = ['ShowPsycStim', 'ShowVevaiometric',
                 'ShowTrialRate', 'ShowFix', 'ShowST', 'ShowFeedback']
    StimDelay = ['StimDelayAutoincrement', 'StimDelayMin', 'StimDelayMax',
                 'StimDelayIncr', 'StimDelayDecr', 'StimDelayGrace',
                 'PreStimuDelayCntrReward']
    StimulusSelection = ['OmegaTable', 'TableNote', 'BetaDistAlphaNBeta',
                         'StimulusSelectionCriteria', 'LeftBias',
                         'LeftBiasVal', 'CorrectBias']
    Vevaiometric = ['VevaiometricYLim', 'VevaiometricMinWT',
                    'VevaiometricNBin', 'VevaiometricShowPoints']
    VisualGeneral = ['VisualStimAnglePortRight', 'VisualStimAnglePortLeft',
                     'screenDistCm', 'screenWidthCm', 'apertureSizeWidth',
                     'apertureSizeHeight', 'centerX', 'centerY']


class GUIMeta:
    class Attribute:
        def __init__(self, Style, String=None, Callback=None):
            self.String = String
            self.Style = Style
            self.Callback = Callback

    class OmegaTableAttribute(Attribute):
        def __init__(self):
            super().__init__('table', String='Omega probabilities')
            self.ColumnEditable = [True, False, True]
            self.ColumnLabel = ['Stim %', 'RDK Coh', 'P(a)']
            self.RDK = GUIMeta.Attribute('text')

    def __init__(self):
        self.AllPerformance = self.Attribute('text')
        self.BeepAfterMinSampling = self.Attribute('checkbox')
        self.CalcLeftBias = self.Attribute('text')
        self.CatchError = self.Attribute('checkbox')
        self.CorrectBias = self.Attribute('checkbox')
        self.CurrentStim = self.Attribute('text')
        self.CutAirReward = self.Attribute('checkbox')
        self.CutAirSampling = self.Attribute('checkbox')
        self.CutAirStimDelay = self.Attribute('checkbox')
        self.ExperimentType = self.Attribute(
            'popupmenu', String=ExperimentType.String())
        self.FeedbackDelay = self.Attribute('text')
        self.FeedbackDelaySelection = self.Attribute(
            'popupmenu', String=FeedbackDelaySelection.String())
        self.HabituateIgnoreIncorrect = self.Attribute('checkbox')
        self.ITISignalType = self.Attribute(
            'popupmenu', String=ITISignalType.String())
        self.IncorrectChoiceSignalType = self.Attribute(
            'popupmenu', String=IncorrectChoiceSignalType.String())
        self.IsCatch = self.Attribute('text')
        self.IsOptoTrial = self.Attribute('text')
        self.LeftBias = self.Attribute('slider', Callback=None)
        self.LeftBiasVal = self.Attribute(None, Callback=None)
        self.MinSample = self.Attribute('text')
        self.MinSampleType = self.Attribute(
            'popupmenu', String=MinSampleType.String())
        self.MouseState = self.Attribute(
            'popupmenu', String=MouseState.String())
        self.OmegaTable = self.OmegaTableAttribute()
        self.OptoBrainRegion = self.Attribute(
            'popupmenu', String=BrainRegion.String())
        self.OptoEndState1 = self.Attribute(
            'popupmenu', String=MatrixState.String())
        self.OptoEndState2 = self.Attribute(
            'popupmenu', String=MatrixState.String())
        self.OptoOr2P = self.Attribute(
            'popupmenu', String=TTLWireUsage.String())
        self.OptoStartState1 = self.Attribute(
            'popupmenu', String=MatrixState.String())
        self.PCTimeout = self.Attribute('checkbox')
        self.Performance = self.Attribute('text')
        self.PlayNoiseforError = self.Attribute('checkbox')
        self.PortLEDtoCueReward = self.Attribute('checkbox')
        self.RewardAfterMinSampling = self.Attribute('checkbox')
        self.ShowFeedback = self.Attribute('checkbox')
        self.ShowFix = self.Attribute('checkbox')
        self.ShowPsycStim = self.Attribute('checkbox')
        self.ShowST = self.Attribute('checkbox')
        self.ShowTrialRate = self.Attribute('checkbox')
        self.ShowVevaiometric = self.Attribute('checkbox')
        self.StimAfterPokeOut = self.Attribute('checkbox')
        self.StimDelay = self.Attribute('text')
        self.StimDelayAutoincrement = self.Attribute(
            'checkbox', String='Auto')
        self.StimulusSelectionCriteria = self.Attribute(
            'popupmenu', String=StimulusSelectionCriteria.String())
        self.TableNote = self.Attribute('text')
        self.VevaiometricShowPoints = self.Attribute('checkbox')
        self.VisualStimAnglePortLeft = self.Attribute(
            'popupmenu', String=VisualStimAngle.String())
        self.VisualStimAnglePortRight = self.Attribute(
            'popupmenu', String=VisualStimAngle.String())
        self.Wire1VideoTrigger = self.Attribute('checkbox')
        self.circleArea = self.Attribute('text')
        self.nDots = self.Attribute('text')


class GUI:
    class OmegaTable:
        def __init__(self):
            self.Omega = list(range(100, 50, -5))
            len_omega = len(self.Omega)
            self.OmegaProb = [len_omega - i - 1 for i in range(len_omega)]
            self.RDK = [(prob - 50) * 2 for prob in self.Omega]

    def __init__(self):
        self.AllPerformance = '(Calc. after 1st trial)'
        self.BeepAfterMinSampling = False
        self.BetaDistAlphaNBeta = 0.3
        self.CalcLeftBias = 0.5
        self.CatchError = False
        self.CenterPokeAttenPrcnt = 95
        self.CenterPortRewAmount = 0.5
        self.ChoiceDeadLine = 20
        self.ComputerName = None
        self.CorrectBias = False
        self.CurrentStim = 0
        self.CutAirReward = False
        self.CutAirSampling = True
        self.CutAirStimDelay = True
        self.ExperimentType = ExperimentType.LightIntensity
        self.FeedbackDelayMax = 1.5
        self.FeedbackDelayMin = 0.5
        self.FeedbackDelay = self.FeedbackDelayMin
        self.FeedbackDelayIncr = 0.01
        self.FeedbackDelayDecr = 0.01
        self.FeedbackDelayTau = 0.1
        self.FeedbackDelayGrace = 0.4
        self.FeedbackDelaySelection = FeedbackDelaySelection.Fix
        self.GUIVer = 29
        self.HabituateIgnoreIncorrect = 0
        self.ITI = 0
        self.ITISignalType = ITISignalType.None_
        self.IncorrectChoiceSignalType = IncorrectChoiceSignalType.BeepOnWire_1
        self.IsCatch = 'false'
        self.IsOptoTrial = 'false'
        self.LeftBias = 0.5
        self.LeftBiasVal = self.LeftBias
        self.LeftPokeAttenPrcnt = 73
        self.MinSampleMax = 0
        self.MinSampleMin = 0
        self.MinSample = self.MinSampleMin
        self.MinSampleDecr = 0.02
        self.MinSampleIncr = 0.05
        self.MinSampleNumInterval = 1
        self.MinSampleRandProb = 0
        self.MinSampleType = MinSampleType.AutoIncr
        self.MouseState = MouseState.FreelyMoving
        self.MouseWeight = None
        self.OmegaTable = self.OmegaTable()
        self.OptoBrainRegion = BrainRegion.V1_L
        self.OptoEndState1 = MatrixState.WaitCenterPortOut
        self.OptoEndState2 = MatrixState.WaitForChoice
        self.OptoMaxTime = 10
        self.OptoOr2P = TTLWireUsage.Optogenetics
        self.OptoProb = 0
        self.OptoStartDelay = 0
        self.OptoStartState1 = MatrixState.stimulus_delivery
        self.PCTimeout = True
        self.Percent50Fifty = 0
        self.PercentCatch = 0
        self.PercentForcedLEDTrial = 0
        self.Performance = '(Calc. after 1st trial)'
        self.PlayNoiseforError = 0
        self.PortLEDtoCueReward = False
        self.Ports_LMRAir = 1238
        self.PreStimuDelayCntrReward = 0
        self.RewardAfterMinSampling = False
        self.RewardAmount = 5
        self.RightPokeAttenPrcnt = 73
        self.ShowFeedback = 1
        self.ShowFix = 1
        self.ShowPsycStim = 1
        self.ShowST = 1
        self.ShowTrialRate = 1
        self.ShowVevaiometric = 1
        self.StartEasyTrials = 10
        self.StimAfterPokeOut = False
        self.StimDelayMax = 0.6
        self.StimDelayMin = 0.3
        self.StimDelay = self.StimDelayMin
        self.StimDelayAutoincrement = 0
        self.StimDelayDecr = 0.01
        self.StimDelayIncr = 0.01
        self.StimDelayGrace = 0.1
        self.StimulusSelectionCriteria = \
            StimulusSelectionCriteria.DiscretePairs
        self.StimulusTime = 0.3
        self.SumRates = 100
        self.TableNote = 'Edit Stim % to update RDK'
        self.TimeOutBrokeFixation = 0
        self.TimeOutEarlyWithdrawal = 0
        self.TimeOutIncorrectChoice = 0
        self.TimeOutMissedChoice = 0
        self.TimeOutSkippedFeedback = 0
        self.VevaiometricMinWT = 0.5
        self.VevaiometricNBin = 8
        self.VevaiometricShowPoints = 1
        self.VevaiometricYLim = 20
        self.VisualStimAnglePortLeft = VisualStimAngle.Degrees270
        self.VisualStimAnglePortRight = VisualStimAngle.Degrees90
        self.Wire1VideoTrigger = False
        self.apertureSizeHeight = 36
        self.apertureSizeWidth = 36
        self.centerX = 0
        self.centerY = 0
        self.circleArea = math.pi * ((self.apertureSizeWidth / 2) ** 2)
        self.cyclesPerSecondDrift = 5
        self.dotLifetimeSecs = 1
        self.dotSizeInDegs = 2
        self.dotSpeedDegsPerSec = 25
        self.drawRatio = 0.2
        self.gaborSizeFactor = 1.2
        self.gaussianFilterRatio = 0.1
        self.nDots = round(self.circleArea * 0.05)
        self.numCycles = 20
        self.phase = 0  # Phase of the wave, goes between 0 to 360
        self.screenDistCm = 30
        self.screenWidthCm = 20


class TaskParameters:
    def __init__(self):
        self.GUI = GUI()
        self.GUIMeta = GUIMeta()
        self.GUIPanels = GUIPanels()
        self.GUITabs = GUITabs()
        self.Figures = Figures()
