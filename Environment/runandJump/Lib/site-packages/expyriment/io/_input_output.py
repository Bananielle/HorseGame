"""
The base module of io.

This module contains the base classes for input and output.

All classes in this module should be called directly via expyriment.io.*.

"""

from __future__ import absolute_import, print_function, division

__author__ = 'Florian Krause <florian@expyriment.org>, \
Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.10.0'
__revision__ = 'bac5b00'
__date__ = 'Wed Oct 30 23:26:23 2019 +0100'


from . import defaults
from .._internals import Expyriment_object


class Input(Expyriment_object):
    """A class implementing a general input."""

    def __init__(self):
        """Create an input."""
        Expyriment_object.__init__(self)


class Output(Expyriment_object):
    """A class implementing a general output."""

    def __init__(self):
        """Create an output."""
        Expyriment_object.__init__(self)
