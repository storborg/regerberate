from .commands import parse_command

default_sentinel = object()


class GerberTokenizer(object):
    """
    Yield each command in the Gerber file, as a tuple including the line
    number it is on. E.g. ``(103, 'D10*')``.
    """
    # XXX This should probably rename to become the GerberTokenizer
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


class GraphicsState(object):
    def __init__(self):
        self.attributes = {}
        self.apertures = {}
        self.aperture_templates = {}

        # Graphics state parameters (see p26 of Gerber spec)

        # Required to be initialized in file.
        self.default_sentinel = default_sentinel
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

    def set_unit(self, unit):
        assert self.unit == default_sentinel, "unit can only be set once"
        self.unit = unit

    def set_coordinate_format(self, integer_digits, fractional_digits):
        assert self.coordinate_format == default_sentinel, \
            "coordinate format can only be set once"
        self.coordinate_format = integer_digits, fractional_digits

    def evaluate_coordinate(self, s):
        """
        Evaluate a coordinate string in the current coordinate format.
        """
        # XXX

    def set_interpolation_mode(self, mode):
        self.interpolation_mode = mode

    def set_quadrant_mode(self, mode):
        self.quadrant_mode = mode

    def set_region_mode(self, mode):
        self.region_mode = mode

    def set_level_polarity(self, polarity):
        self.level_polarity = polarity

    def set_current_aperture(self, aperture_number):
        # XXX
        pass


class GraphicsPlane(object):
    pass


class GerberParser(object):
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        plane = GraphicsPlane()
        state = GraphicsState()

        with open(self.filename, 'rU') as f:
            raw_width = 36
            print('Line\t%s\tResult' % "Raw".ljust(raw_width))
            print('----\t%s\t-----------' % ('-' * raw_width))
            for line_no, s in GerberTokenizer(f):
                cmd = parse_command(s)
                assert cmd.to_string() == s
                print("%04d\t%s\t%r" % (line_no, s.ljust(raw_width), cmd))
                cmd.execute(state, plane)

        return plane
