"""
Table of command codes is in Section 4.1, page 58.
"""
import re
from decimal import Decimal


def parse_command(s):
    if s[0] == '%':
        # Extended commands, identify by first 3 chars
        code = s[1:3]
        cls = extended_commands[code]
        return cls.from_string(s)
    else:
        # For normal commands, identify by end
        code = s[-4:-1]
        if code in normal_commands:
            cls = normal_commands[code]
            return cls.from_string(s)
        else:
            # If not in the map it's a set aperture command
            return SetApertureCommand.from_string(s)


class Command(object):
    """
    Base class for Gerber commands.
    """
    deprecated = False

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__dict__)

    @classmethod
    def from_string(cls, s):
        return cls()

    def execute(self, state, plane):
        # XXX This should go away!
        pass


class UnitCommand(Command):
    """
    Command Code MO - Extended
    Section 4.10, p98
    """
    def __init__(self, unit):
        self.unit = unit

    @classmethod
    def from_string(cls, s):
        unit = s[3:5]
        assert unit in ('IN', 'MM'), "invalid unit %r" % unit
        return cls(unit=unit)

    def to_string(self):
        return '%MO' + self.unit + '*%'

    def execute(self, state, plane):
        assert state.unit == state.default_sentinel, \
            "unit can only be set once"
        state.unit = self.unit


class CoordinateFormatCommand(Command):
    """
    Command Code FS - Extended
    Section 4.9, p96
    """
    def __init__(self, integer_digits, fractional_digits):
        self.integer_digits = integer_digits
        self.fractional_digits = fractional_digits

    @classmethod
    def from_string(cls, s):
        assert s.startswith('%FSLAX')
        xformat = s[6:8]
        yformat = s[9:11]
        assert xformat == yformat
        return cls(integer_digits=int(xformat[0]),
                   fractional_digits=int(xformat[1]))

    def to_string(self):
        format = '%d%d' % (self.integer_digits, self.fractional_digits)
        return '%FSLAX' + format + 'Y' + format + '*%'


class OffsetCommand(Command):
    """
    Comamnd Code OF - Extended, Deprecated
    Section 7.1.7, p163
    Syntax is like %OFA1.2B-1.0*%
    """
    deprecated = True

    def __init__(self, offset_a, offset_b):
        self.offset_a = offset_a
        self.offset_b = offset_b

    @classmethod
    def from_string(cls, s):
        assert s.startswith('%OFA')
        format = s[4:-2]
        raw_a, raw_b = format.split('B')
        offset_a = Decimal(raw_a)
        offset_b = Decimal(raw_b)
        return cls(offset_a=offset_a, offset_b=offset_b)

    def to_string(self):
        return '%OFA' + str(self.offset_a) + 'B' + str(self.offset_b) + '*%'


class ImagePolarityCommand(Command):
    """
    Command Code IP - Extended, Deprecated
    Section 7.1.3, p160
    """
    deprecated = True

    def __init__(self, polarity):
        self.polarity = polarity

    @classmethod
    def from_string(cls, s):
        polarity = s[3:-2]
        assert polarity in ('POS', 'NEG')
        return cls(polarity=polarity)

    def to_string(self):
        return '%IP' + self.polarity + '*%'


class LevelPolarityCommand(Command):
    """
    Command Code LP - Extended
    Section 4.15.1, p132
    Syntax is like %LPD*% or %LPC*%
    C = clear
    D = dark
    """
    def __init__(self, polarity):
        self.polarity = polarity

    @classmethod
    def from_string(cls, s):
        polarity = s[3]
        assert polarity in ('D', 'C')
        return cls(polarity=polarity)

    def to_string(self):
        return '%LP' + self.polarity + '*%'


class MacroApertureCommand(Command):
    """
    Command Code AM - Extended
    Section 4.13.1 - p106
    Syntax is complex, return to this later
    """
    # XXX This is missing a lot of stuff
    def __init__(self, template_name, s):
        self.template_name = template_name
        self.s = s

    @classmethod
    def from_string(cls, s):
        assert s.startswith('%AM')
        template_name = s.split('*', 1)[0][3:]
        return cls(template_name=template_name,
                   s=s)

    def to_string(self):
        return self.s


class ApertureDefinitionCommand(Command):
    """
    Comamnd Code AD - Extended
    Section 4.11.1 p p99
    Syntax is complex, return to this later

    Aperture definitions can either include relevant information directly, or
    can reference a named aperture macro created by a MacroApertureCommand.
    """
    # XXX This is missing a lot of stuff
    def __init__(self, aperture_number, template_name, s):
        self.aperture_number = aperture_number
        self.template_name = template_name
        self.s = s

    @classmethod
    def from_string(cls, s):
        assert s.startswith('%ADD')
        content = s[4:-2]
        m = re.match('^(\d+)([a-zA-Z_.]+)', content)
        aperture_number = int(m.group(1))
        template_name = m.group(2)
        return cls(aperture_number=aperture_number,
                   template_name=template_name,
                   s=s)

    def to_string(self):
        return self.s


class SetApertureCommand(Command):
    """
    Command Code Dnnnn
    Section 4.3.1, p64
    Syntax is like Dnnn*
    """
    def __init__(self, aperture_number):
        assert aperture_number >= 10
        self.aperture_number = aperture_number

    @classmethod
    def from_string(cls, s):
        aperture_number = int(s[1:-1])
        return cls(aperture_number=aperture_number)

    def to_string(self):
        return 'D' + str(self.aperture_number) + '*'


class InterpolateCommand(Command):
    """
    Command Code D01
    Section 4.2.2, p61
    Syntax is like XnnnYnnnInnnJnnnD01* in circular interpolation modes
    Syntax is like XnnnYnnnD01* in linear interpolation mode

    XnnnYnnn indicates the end point
    InnnJnnn indicates the center point offsets in circular modes
    """
    def __init__(self, x_string, y_string, i_string=None, j_string=None):
        self.x_string = x_string
        self.y_string = y_string
        self.i_string = i_string
        self.j_string = j_string

    @classmethod
    def from_string(cls, s):
        if 'I' in s:
            m = re.match('X(\d+)Y(\d+)I(\d+)J(\d+)', s)
            x_string = m.group(1)
            y_string = m.group(2)
            i_string = m.group(3)
            j_string = m.group(4)
            return cls(x_string=x_string, y_string=y_string,
                       i_string=i_string, j_string=j_string)
        else:
            m = re.match('X(\d+)Y(\d+)', s)
            x_string = m.group(1)
            y_string = m.group(2)
            return cls(x_string=x_string, y_string=y_string)

    def to_string(self):
        if self.i_string:
            return 'X%sY%sI%sJ%sD01*' % (self.x_string, self.y_string,
                                         self.i_string, self.j_string)
        else:
            return 'X%sY%sD01*' % (self.x_string, self.y_string)


class MoveCommand(Command):
    """
    Command Code D02
    Section 4.2.3, p62
    Syntax is like XnnnYnnnD02*
    """
    def __init__(self, x_string, y_string):
        self.x_string = x_string
        self.y_string = y_string

    @classmethod
    def from_string(cls, s):
        raw = s[1:-4]
        x_string, y_string = raw.split('Y')
        return cls(x_string=x_string, y_string=y_string)

    def to_string(self):
        return 'X' + self.x_string + 'Y' + self.y_string + 'D02*'


class FlashCommand(Command):
    """
    Command Code D03
    Section 4.2.4, p62
    Syntax is like XnnnYnnnD03*
    """
    def __init__(self, x_string, y_string):
        self.x_string = x_string
        self.y_string = y_string

    @classmethod
    def from_string(cls, s):
        raw = s[1:-4]
        x_string, y_string = raw.split('Y')
        return cls(x_string=x_string, y_string=y_string)

    def to_string(self):
        return 'X' + self.x_string + 'Y' + self.y_string + 'D03*'


class LinearInterpolationModeCommand(Command):
    """
    Command Code G01
    Section 4.4.1, p65
    No args
    """
    def to_string(self):
        return 'G01*'


class CWCircularInterpolationModeCommand(Command):
    """
    Command Code G02
    Section 4.5.3, p68
    No args
    """
    def to_string(self):
        return 'G02*'


class CCWCircularInterpolationModeCommand(Command):
    """
    Command Code G03
    Section 4.5.4, p68
    No args
    """
    def to_string(self):
        return 'G03*'


class SingleQuadrantCommand(Command):
    """
    Command Code G74
    Section 4.5.5, p68
    No args
    """
    def to_string(self):
        return 'G74*'


class MultiQuadrantCommand(Command):
    """
    Command Code G75
    Section 4.5.6, p68
    No args
    """
    def to_string(self):
        return 'G75*'


class EnableRegionModeCommand(Command):
    """
    Command Code G36
    Section 4.6.2, p76
    No args
    """
    def to_string(self):
        return 'G36*'


class DisableRegionModeCommand(Command):
    """
    Command Code G37
    Section 4.6.3, p76
    No args
    """
    def to_string(self):
        return 'G37*'


class CommentCommand(Command):
    """
    Command Code G04
    Section 4.7, p94
    """
    def __init__(self, comment):
        self.comment = comment

    @classmethod
    def from_string(cls, s):
        comment = s[3:-1]
        return cls(comment=comment)

    def to_string(self):
        return 'G04' + self.comment + '*'


class EOFCommand(Command):
    """
    Command Code M02
    No args
    """
    def to_string(self):
        return 'M02*'


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
