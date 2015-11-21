Quick Start
===========

Install
-------

Install with pip::

    $ pip install regerberate


Workflow
--------

The goal of the Regerberate workflow is to make it easy and fast to use an SVG editor to edit layers in a PCB layout, while enabling version control, single-step production builds, and flexibility between EDA packages.

The typical workflow looks like this:

Initial Board Design
~~~~~~~~~~~~~~~~~~~~

Use any EDA package to design a board. The board shouldn't include elements
which will be edited in SVG tools: in order to avoid "redoing" work when edits
are made in the source EDA package, additional SVG artwork should only be
composited, and not subtract from or mutate "base" art.

Generate a set of base Gerber files from the EDA tool. This is identical to the
process that you would normally use to generate Gerber files for production.

SVG File Creation
~~~~~~~~~~~~~~~~~

Call regerberate on the set of Gerber files to build an SVG.::

    $ regerberate prepare -o myboard.svg intermediate/*.ger

For each source Gerber file, a pair of layers will be created in the SVG file.

One layer in the pair is the *base* layer as output by the EDA package. It
should generally not be modified, and just serves as a visual reference to
design other art around. Regerberate can update this layer based on new Gerbers
exported by the EDA package.

The other layer in the pair is the *extra* layer, and is where additional
artwork should be added.

SVG Editing
~~~~~~~~~~~

Drawing primitives in the *extra* SVG layers will be replicated in the
output Gerber files. A wide variety of SVG features cannot be translated into
the Gerber format, like colors and zero-width lines. These should be avoided.

Rendering of SVG to Gerber
~~~~~~~~~~~~~~~~~~~~~~~~~~

The SVG file can then be rendered into a new set of output Gerber files ready
for production.::

    $ regerberate render -o build/ myboard.svg

Each Gerber file will contain the composite of the corresponding *base* and
*extra* SVG layer pair. Gerber filenames will be preserved from the
intermediate Gerber files used to create them.
