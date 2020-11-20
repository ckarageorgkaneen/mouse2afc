from .special_enum import SpecialEnum


class VisualStimAngle(SpecialEnum):
    Degrees0 = 1
    Degrees45 = 2
    Degrees90 = 3
    Degrees135 = 4
    Degrees180 = 5
    Degrees225 = 6
    Degrees270 = 7
    Degrees315 = 8

    @staticmethod
    def get_degrees(variable_index):
        return (variable_index - 1) * 45
