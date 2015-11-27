import logging

import os.path
from collections import OrderedDict

from .gerber.context import Context
from .gerber.parser import GerberParser

log = logging.getLogger(__name__)


class LayerSet(object):

    def __init__(self):
        self.layers = OrderedDict()

    @classmethod
    def load_svg(cls, filename):
        log.debug('load_svg(%s)', filename)

    def write_svg(self, filename):
        log.debug('write_svg(%s)', filename)

    def update_from_gerber(self, filename):
        log.debug('update_from_gerber(%s)', filename)
        new_base_layer = self.gerber_read(filename)
        name = filename[:-4]

        if name in self.layers:
            base_layer, extra_layer = self.layers[name]
            self.layers[name] = new_base_layer, extra_layer
        else:
            self.layers[name] = new_base_layer, None

    def render_gerbers(self, output_path):
        log.debug('render_gerbers(%s)', output_path)
        for name, (base_layer, extra_layer) in self.layers.items():
            layer = self.composite(base_layer, extra_layer)
            filename = os.path.join(output_path, name + '.ger')
            self.gerber_write(layer, filename)

    def composite(self, bottom, top):
        pass

    def gerber_read(self, filename):
        context = Context()
        GerberParser(filename, context).parse()
        return context

    def gerber_write(self, layer, filename):
        pass
