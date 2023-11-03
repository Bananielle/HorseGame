"""The design package.

This package provides several data structures for describing the design of an
experiment.  See also expyriment.design.extras for more design.

"""

__author__ = 'Florian Krause <florian@expyriment.org> \
              Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.10.0'
__revision__ = 'bac5b00'
__date__ = 'Wed Oct 30 23:26:23 2019 +0100'


from . import defaults
from . import permute
from . import randomize
from ._structure import Experiment, Block, Trial

from .. import _internals
_internals.active_exp = Experiment("None")

