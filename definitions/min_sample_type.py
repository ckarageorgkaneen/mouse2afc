from .special_enum import SpecialEnum


class MinSampleType(SpecialEnum):
    FixMin = 1
    AutoIncr = 2
    RandBetMinMax_DefIsMax = 3
    RandNumIntervalsMinMax_DefIsMax = 4
