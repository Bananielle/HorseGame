"""The expyriment randomize module.

This module contains various functions for randomizing data

"""

__author__ = 'Florian Krause <florian@expyriment.org>,\
              Oliver Lindemann <oliver@expyriment.org>'
__version__ = '0.10.0'
__revision__ = 'bac5b00'
__date__ = 'Wed Oct 30 23:26:23 2019 +0100'


from ._randomize import rand_int_sequence, rand_int, rand_element, rand_norm
from ._randomize import coin_flip, shuffle_list, make_multiplied_shuffled_list
