from .commands import parse_command

default_sentinel = object()


class Tokenizer(object):
    """
    Yield each command in the Gerber file, as a tuple including the line
    number it is on. E.g. ``(103, 'D10*')``.
    """
    def __init__(self, f):
        self.f = f
        self.inside_extended = False
        self.current_command = ''
        self.line_no = 1

    def __iter__(self):
        while True:
            c = self.f.read(1)
            if not c:
                break
            if c == '\n':
                self.line_no += 1
            else:
                self.current_command += c
            if c == '%':
                if self.inside_extended:
                    yield self.line_no, self.current_command
                    self.current_command = ''
                    self.inside_extended = False
                else:
                    self.inside_extended = True
            elif (c == '*') and (not self.inside_extended):
                yield self.line_no, self.current_command
                self.current_command = ''


class GerberParser(object):
    def __init__(self, filename, context):
        self.filename = filename
        self.context = context

        self.attributes = {}
        # XXX Maybe this should go away?
        self.commands = []

        # Graphics state parameters (see p26 of Gerber spec)

        # Required to be initialized in file.
        self.coordinate_format = default_sentinel
        self.unit = default_sentinel
        self.current_aperture = default_sentinel
        self.quadrant_mode = default_sentinel
        self.interpolation_mode = default_sentinel

        # Optional: can use default.
        self.current_point = (0, 0)
        self.step_and_repeat = (1, 1, 0, 0)
        self.level_polarity = 'dark'
        self.region_mode = 'off'

    def parse(self):
        with open(self.filename, 'rU') as f:
            raw_width = 36
            print('Line\t%s\tResult' % "Raw".ljust(raw_width))
            print('----\t%s\t-----------' % ('-' * raw_width))
            for line_no, s in Tokenizer(f):
                cmd = parse_command(s)
                assert cmd.to_string() == s
                print("%04d\t%s\t%r" % (line_no, s.ljust(raw_width), cmd))
                self.commands.append(cmd)
