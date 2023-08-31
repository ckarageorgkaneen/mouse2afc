from mouse2afc.definitions.special_enum import SpecialEnum


class MatrixState(SpecialEnum):
    ITI_Signal = 1
    WaitForCenterPoke = 2
    PreStimReward = 3
    TriggerWaitForStimulus = 4
    WaitForStimulus = 5
    StimDelayGrace = 6
    BrokeFixation = 7
    StimulusDelivery = 8
    EarlyWithdrawal = 9
    BeepMinSampling = 10
    CenterPortRewardDelivery = 11
    TriggerWaitChoiceTimer = 12
    WaitCenterPortOut = 13
    WaitForChoice = 14
    WaitForRewardStart = 15
    WaitForReward = 16
    RewardGrace = 17
    Reward = 18
    WaitRewardOut = 19
    RegisterWrongWaitCorrect = 20
    WaitForPunishStart = 21
    WaitForPunish = 22
    PunishGrace = 23
    Punishment = 24
    TimeoutEarlyWithdrawal = 25
    TimeoutEarlyWithdrawalFlashOn = 26
    TimeoutIncorrectChoice = 27
    TimeoutSkippedFeedback = 28
    TimeoutMissedChoice = 29
    ITI = 30
    ext_ITI = 31
    WaitPunishOut = 32
    #WaitPunishEnd = 33
    StimulusTime = 34
    #triggerTimoutIncorrectChoice = 35
    #TODO find out if 33 and 35 need to be here or if they can be deleted
    