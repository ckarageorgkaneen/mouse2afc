from .special_enum import SpecialEnum


class FeedbackDelaySelection(SpecialEnum):
    Fix = 1
    AutoIncr = 2
    TruncExp = 3
    None_ = 4
