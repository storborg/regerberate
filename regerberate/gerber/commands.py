"""
Table of command codes is in Section 4.1, page 58.
"""


class Command(object):
    deprecated = False

    def __init__(self, s):
        self.s = s

    def __str__(self):
        return self.s

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.s)

    @staticmethod
    def from_string(s):
        if s[0] == '%':
            # Extended commands, identify by first 3 chars
            code = s[1:3]
            cls = extended_commands[code]
            return cls(s)
        else:
            # For normal commands, identify by end
            code = s[-4:-1]
            if code in normal_commands:
                cls = normal_commands[code]
                return cls(s)
            else:
                # If not in the map it's a set aperture command
                return SetApertureCommand(s)


class UnitCommand(Command):
    # MO, extended
    # Section 4.10, p98
    def __init__(self, s):
        Command.__init__(self, s)
        self.units = s[3:5]


class CoordinateFormatCommand(Command):
    # FS, extended
    # Section 4.9, p96
    def __init__(self, s):
        Command.__init__(self, s)
        assert s.startswith('%FSLAX')
        xformat = s[6:8]
        yformat = s[9:11]
        assert xformat == yformat
        self.format = xformat


class OffsetCommand(Command):
    deprecated = True
    # OF, extended, deprecated
    # Section 7.1.7, p163
    pass


class ImagePolarityCommand(Command):
    deprecated = True
    # IP, extended, deprecated
    # Section 7.1.3, p160
    pass


class LevelPolarityCommand(Command):
    # LP, extended
    # Section 4.15.1, p132
    pass


class MacroApertureCommand(Command):
    # AM, extended
    # Section 4.13 - p106
    pass


class ApertureDefinitionCommand(Command):
    # AD, extended
    # Section 4.11 p p99
    pass


class SetApertureCommand(Command):
    # Dnnnn
    # Section 4.3.1, p64
    # Syntax is like Dnnn
    pass


class InterpolateCommand(Command):
    # D01
    # Section 4.2.2, p61
    # Syntax is like XnnnYnnnInnnJnnnD01* in normal mode
    # Syntax is like XnnnYnnnD01* in linear interpolation mode
    pass


class MoveCommand(Command):
    # D02
    # Section 4.2.3, p62
    # Syntax is like XnnnYnnnD02*
    pass


class FlashCommand(Command):
    # D03
    # Section 4.2.4, p62
    # Syntax is like XnnnYnnnD03*
    pass


class LinearInterpolationModeCommand(Command):
    # G01
    # Section 4.4.1, p65
    pass


class CWCircularInterpolationModeCommand(Command):
    # G02
    # Section 4.5.3, p68
    pass


class CCWCircularInterpolationModeCommand(Command):
    # G03
    # Section 4.5.4, p68
    pass


class SingleQuadrantCommand(Command):
    # G74
    # Section 4.5.5, p68
    pass


class MultiQuadrantCommand(Command):
    # G75
    # Section 4.5.6, p68
    pass


class EnableRegionModeCommand(Command):
    # G36
    # Section 4.6.2, p76
    pass


class DisableRegionModeCommand(Command):
    # G37
    # Section 4.6.3, p76
    pass


class CommentCommand(Command):
    # G04
    # Section 4.7, p94
    pass


class EOFCommand(Command):
    # M02
    pass


extended_commands = {
    'MO': UnitCommand,
    'FS': CoordinateFormatCommand,
    'OF': OffsetCommand,
    'IP': ImagePolarityCommand,
    'LP': LevelPolarityCommand,
    'AM': MacroApertureCommand,
    'AD': ApertureDefinitionCommand,
}


normal_commands = {
    'D01': InterpolateCommand,
    'D02': MoveCommand,
    'D03': FlashCommand,
    'G01': LinearInterpolationModeCommand,
    'G02': CWCircularInterpolationModeCommand,
    'G03': CCWCircularInterpolationModeCommand,
    'G74': SingleQuadrantCommand,
    'G75': MultiQuadrantCommand,
    'G36': EnableRegionModeCommand,
    'G37': DisableRegionModeCommand,
    'G04': CommentCommand,
    'M02': EOFCommand,
}
