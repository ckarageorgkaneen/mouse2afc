from enum import Enum


class SpecialEnumMeta(type(Enum)):
    def __str__(cls):
        return ' '.join(cls.members())

    def String(cls):
        return cls.members()

    def members(cls):
        return list(dict(cls.__members__).keys())


class SpecialEnum(Enum, metaclass=SpecialEnumMeta):
    def __str__(self):
        return self.name
