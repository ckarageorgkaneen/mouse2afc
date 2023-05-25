from .special_enum import SpecialEnum


class StimAfterPokeOut(SpecialEnum):
    NotUsed = 1
    UntilFeedbackStart = 2
    UntilFeedbackEnd = 3
    UntilEndofTrial = 4