from mouse2afc.definitions.special_enum import SpecialEnum


class VisualStimAngle(SpecialEnum):
    degrees_0 = 1
    degrees_45 = 2
    degrees_90 = 3
    degrees_135 = 4
    degrees_180 = 5
    degrees_225 = 6
    degrees_270 = 7
    degrees_315 = 8

    @staticmethod
    def get_degrees(variable_index):
        return (variable_index - 1) * 45
