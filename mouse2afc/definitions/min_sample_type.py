from mouse2afc.definitions.special_enum import SpecialEnum


class MinSampleType(SpecialEnum):
    fix_min = 1
    auto_incr = 2
    rand_bet_min_max_def_is_max = 3
    rand_num_intervals_min_max_def_is_max = 4
