import logging

import sys
import argparse
import os.path

from .layerset import LayerSet

log = logging.getLogger(__name__)


def prepare(opts):
    if os.path.exists(opts.output):
        layers = LayerSet.load_file(opts.output)
    else:
        layers = LayerSet()

    for filename in opts.inputs:
        layers.update_from_gerber(filename)

    layers.write_file(opts.output)
    return 0


def render(opts):
    layers = LayerSet.load_file(opts.input)
    layers.render_gerbers(opts.output)
    return 0


def main(argv=sys.argv):
    p = argparse.ArgumentParser(description='Design PCB Art with SVG Tools.')

    subparsers = p.add_subparsers(help='sub-command help')

    p_prepare = subparsers.add_parser(
        'prepare',
        help='Prepare or update SVG file from intermediate Gerbers.')
    p_prepare.add_argument('inputs', nargs='*')
    p_prepare.add_argument('-o', '--output', dest='output',
                           default='board.svg')
    p_prepare.set_defaults(function=prepare)

    p_render = subparsers.add_parser(
        'render',
        help='Render output Gerbers from an SVG file.')
    p_render.add_argument('input')
    p_render.add_argument('-o', '--output', dest='output')
    p_render.set_defaults(function=render)

    logging.basicConfig(level=logging.DEBUG)

    opts, args = p.parse_known_args(argv[1:])
    return opts.function(opts)
