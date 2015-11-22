import logging

import os.path
from collections import OrderedDict

log = logging.getLogger(__name__)


def composite(a, b):
    pass


def gerber_write(layer, filename):
    pass


def gerber_read(filename):
    pass


class LayerSet(object):

    def __init__(self):
        self.layers = OrderedDict()

    @classmethod
    def load_file(cls, filename):
        log.debug('load_file(%s)', filename)
        pass

    def write_file(self, filename):
        log.debug('write_file(%s)', filename)
        pass

    def update_from_gerber(self, filename):
        log.debug('update_from_gerber(%s)', filename)
        new_base_layer = gerber_read(filename)
        name = filename[:-4]

        if name in self.layers:
            base_layer, extra_layer = self.layers[name]
            self.layers[name] = new_base_layer, extra_layer
        else:
            self.layers[name] = new_base_layer, None

    def render_gerbers(self, output_path):
        log.debug('render_gerbers(%s)', output_path)
        for name, (base_layer, extra_layer) in self.layers.items():
            layer = composite(base_layer, extra_layer)
            filename = os.path.join(output_path, name + '.ger')
            gerber_write(layer, filename)
